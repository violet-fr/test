"""通知公告 API

对应 P3 任务：公告发布与已读未读统计。

接口清单：
- GET    /notices               公告列表（支持 status/type 筛选）
- GET    /notices/{id}          公告详情（调用即自动标记当前用户已读）
- POST   /notices               发布公告
- PUT    /notices/{id}          修改公告
- DELETE /notices/{id}          删除公告
- GET    /notices/{id}/read-stat 已读未读统计

错误码段：20000-20999（20001 = 公告不存在）。
权限码：oa:notice:{list/add/edit/delete}。
"""
from datetime import datetime

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.dependencies import get_current_user, require_permissions
from app.core.exceptions import BizException
from app.core.response import page_success, success
from app.models.notice import Notice
from app.models.notice_read import NoticeRead
from app.models.user import User
from app.schemas.notice import (
    NoticeCreate,
    NoticeOut,
    NoticeUpdate,
    ReadStatOut,
    UnreadUserOut,
)

router = APIRouter(prefix="/notices", tags=["通知公告"])


@router.get("")
def list_notices(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    title: str = Query(None, description="标题模糊筛选"),
    type: str = Query(None, description="类型筛选 notice/announcement"),
    status: int = Query(None, description="状态筛选 0草稿/1已发布"),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permissions(["oa:notice:list"])),
):
    """公告列表

    - 后台管理：不传 status 即返回全部
    - 小程序端：传 status=1 仅返回已发布
    """
    query = db.query(Notice)
    if title:
        query = query.filter(Notice.title.contains(title))
    if type:
        query = query.filter(Notice.type == type)
    if status is not None:
        query = query.filter(Notice.status == status)

    # 按 publish_time 倒序，未发布的排在其后
    query = query.order_by(Notice.publish_time.desc().nullslast(), Notice.id.desc())
    total = query.count()
    items = query.offset((page - 1) * page_size).limit(page_size).all()
    return page_success([NoticeOut.from_orm(n) for n in items], total, page, page_size)


@router.get("/{notice_id}")
def get_notice(
    notice_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """公告详情

    P3 特性：调用详情即自动为当前用户标记已读（若未读过）。
    草稿状态的公告不触发已读记录（避免污染统计）。
    """
    notice = db.query(Notice).filter(Notice.id == notice_id).first()
    if not notice:
        raise BizException(20001, "公告不存在")

    # 仅已发布公告才记录已读
    if notice.status == 1:
        existing = db.query(NoticeRead).filter(
            NoticeRead.notice_id == notice_id,
            NoticeRead.user_id == current_user.id,
        ).first()
        if not existing:
            db.add(NoticeRead(notice_id=notice_id, user_id=current_user.id))
            db.commit()

    return success(NoticeOut.from_orm(notice))


@router.post("")
def create_notice(
    req: NoticeCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permissions(["oa:notice:add"])),
):
    """发布公告

    status=1 表示直接发布，自动写入 publish_time 和 publisher_id；
    status=0 表示存为草稿，publish_time 留空。
    """
    notice = Notice(
        title=req.title,
        content=req.content,
        type=req.type,
        status=req.status,
        publisher_id=current_user.id,
        publish_time=datetime.now() if req.status == 1 else None,
    )
    db.add(notice)
    db.commit()
    db.refresh(notice)
    return success(NoticeOut.from_orm(notice))


@router.put("/{notice_id}")
def update_notice(
    notice_id: int,
    req: NoticeUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permissions(["oa:notice:edit"])),
):
    """修改公告

    草稿转为已发布（status 0→1）时自动补充 publish_time 与 publisher_id。
    """
    notice = db.query(Notice).filter(Notice.id == notice_id).first()
    if not notice:
        raise BizException(20001, "公告不存在")

    data = req.dict(exclude_unset=True)
    # 捕获状态变更：0->1 视为首次发布
    becoming_published = data.get("status") == 1 and notice.status != 1
    for k, v in data.items():
        setattr(notice, k, v)
    if becoming_published:
        notice.publish_time = datetime.now()
        notice.publisher_id = current_user.id

    db.commit()
    db.refresh(notice)
    return success(NoticeOut.from_orm(notice))


@router.delete("/{notice_id}")
def delete_notice(
    notice_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permissions(["oa:notice:delete"])),
):
    """删除公告

    同步删除该公告的阅读回执记录，避免统计脏数据。
    """
    notice = db.query(Notice).filter(Notice.id == notice_id).first()
    if not notice:
        raise BizException(20001, "公告不存在")
    # 删除关联的阅读回执
    db.query(NoticeRead).filter(NoticeRead.notice_id == notice_id).delete()
    db.delete(notice)
    db.commit()
    return success()


@router.get("/{notice_id}/read-stat")
def get_read_stat(
    notice_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permissions(["oa:notice:list"])),
):
    """已读未读统计

    - total：应读总人数（启用状态的系统用户数）
    - read_count：已读人数（biz_notice_read 中该 notice_id 的记录数）
    - unread_count：未读人数 = total - read_count
    - unread_users：未读人员列表（左连接 NoticeRead 为 null 的用户）
    """
    notice = db.query(Notice).filter(Notice.id == notice_id).first()
    if not notice:
        raise BizException(20001, "公告不存在")

    # 应读总人数：启用状态的用户
    total = db.query(User).filter(User.status == 1).count()

    # 已读人数
    read_count = db.query(NoticeRead).filter(
        NoticeRead.notice_id == notice_id
    ).count()

    # 未读人员列表：User 左连接 NoticeRead，过滤出没有阅读记录的用户
    unread_users = (
        db.query(User)
        .outerjoin(NoticeRead, (NoticeRead.user_id == User.id) & (NoticeRead.notice_id == notice_id))
        .filter(User.status == 1, NoticeRead.id.is_(None))
        .all()
    )

    return success(ReadStatOut(
        notice_id=notice_id,
        total=total,
        read_count=read_count,
        unread_count=total - read_count,
        unread_users=[UnreadUserOut.from_orm(u) for u in unread_users],
    ).dict())
