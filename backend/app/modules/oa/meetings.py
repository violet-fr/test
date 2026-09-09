"""会议室预约 API

对应 P3 任务：会议室预约（冲突检测）。

接口清单：
- GET    /meeting-rooms            会议室列表
- POST   /meeting-rooms            新增会议室
- PUT    /meeting-rooms/{id}       修改会议室
- DELETE /meeting-rooms/{id}       删除会议室
- GET    /meeting-rooms/{id}/bookings  某会议室预约记录
- GET    /bookings                预约列表（按日期/会议室筛选）
- POST   /bookings                预约会议室（含时间冲突检测）
- DELETE /bookings/{id}            取消预约

错误码段：20030-20049（会议室相关）。
权限码：oa:meeting:{list/add/edit/delete}。

冲突检测算法（区间半开 [start, end)）：
  新预约与已有预约重叠的条件：
  newStart < existEnd AND newEnd > existStart
  相邻时段不冲突（如 [9,10) 和 [10,11) 可同时预约）。
"""
from datetime import datetime, date

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.dependencies import get_current_user, require_permissions
from app.core.exceptions import BizException
from app.core.response import page_success, success
from app.models.meeting import Booking, MeetingRoom
from app.models.user import User
from app.schemas.meeting import (
    BookingCreate,
    BookingOut,
    RoomCreate,
    RoomOut,
    RoomUpdate,
)

router = APIRouter(tags=["会议室预约"])

# 预约状态
BOOKING_ACTIVE = 1    # 已预约
BOOKING_CANCELLED = 2  # 已取消


# ====================================================================
# 会议室 CRUD
# ====================================================================
@router.get("/meeting-rooms")
def list_rooms(
    name: str = Query(None, description="名称模糊筛选"),
    status: int = Query(None, description="状态筛选 1可用 0停用"),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permissions(["oa:meeting:list"])),
):
    """会议室列表"""
    query = db.query(MeetingRoom)
    if name:
        query = query.filter(MeetingRoom.name.contains(name))
    if status is not None:
        query = query.filter(MeetingRoom.status == status)
    items = query.order_by(MeetingRoom.id.desc()).all()
    return success([RoomOut.from_orm(r) for r in items])


@router.post("/meeting-rooms")
def create_room(
    req: RoomCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permissions(["oa:meeting:add"])),
):
    """新增会议室"""
    room = MeetingRoom(
        name=req.name,
        location=req.location,
        capacity=req.capacity,
        equipment=req.equipment,
        status=req.status,
    )
    db.add(room)
    db.commit()
    db.refresh(room)
    return success(RoomOut.from_orm(room))


@router.put("/meeting-rooms/{room_id}")
def update_room(
    room_id: int,
    req: RoomUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permissions(["oa:meeting:edit"])),
):
    """修改会议室"""
    room = db.query(MeetingRoom).filter(MeetingRoom.id == room_id).first()
    if not room:
        raise BizException(20030, "会议室不存在")

    data = req.dict(exclude_unset=True)
    for k, v in data.items():
        setattr(room, k, v)

    db.commit()
    db.refresh(room)
    return success(RoomOut.from_orm(room))


@router.delete("/meeting-rooms/{room_id}")
def delete_room(
    room_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permissions(["oa:meeting:delete"])),
):
    """删除会议室

    如果该会议室存在未取消的预约，阻止删除（避免预约记录变成孤儿）。
    """
    room = db.query(MeetingRoom).filter(MeetingRoom.id == room_id).first()
    if not room:
        raise BizException(20030, "会议室不存在")

    active_count = db.query(Booking).filter(
        Booking.room_id == room_id,
        Booking.status == BOOKING_ACTIVE,
    ).count()
    if active_count > 0:
        raise BizException(20031, f"该会议室有 {active_count} 条未取消预约，无法删除")

    db.delete(room)
    db.commit()
    return success()


@router.get("/meeting-rooms/{room_id}/bookings")
def list_room_bookings(
    room_id: int,
    booking_date: date = Query(None, description="按日期筛选(YYYY-MM-DD)"),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permissions(["oa:meeting:list"])),
):
    """某会议室的预约记录"""
    room = db.query(MeetingRoom).filter(MeetingRoom.id == room_id).first()
    if not room:
        raise BizException(20030, "会议室不存在")

    query = db.query(Booking).filter(Booking.room_id == room_id)
    if booking_date:
        # 当天 00:00:00 ~ 次日 00:00:00
        day_start = datetime.combine(booking_date, datetime.min.time())
        day_end = datetime.combine(booking_date, datetime.max.time())
        query = query.filter(Booking.start_time >= day_start, Booking.start_time <= day_end)

    items = query.order_by(Booking.start_time).all()
    return success([BookingOut.from_orm(b) for b in items])


# ====================================================================
# 预约
# ====================================================================
@router.get("/bookings")
def list_bookings(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    room_id: int = Query(None, description="按会议室筛选"),
    booking_date: date = Query(None, description="按日期筛选(YYYY-MM-DD)"),
    status: int = Query(None, description="状态筛选 1已预约 2已取消"),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permissions(["oa:meeting:list"])),
):
    """预约列表（按日期/会议室筛选）"""
    query = db.query(Booking)
    if room_id:
        query = query.filter(Booking.room_id == room_id)
    if booking_date:
        day_start = datetime.combine(booking_date, datetime.min.time())
        day_end = datetime.combine(booking_date, datetime.max.time())
        query = query.filter(Booking.start_time >= day_start, Booking.start_time <= day_end)
    if status is not None:
        query = query.filter(Booking.status == status)

    query = query.order_by(Booking.start_time.desc())
    total = query.count()
    items = query.offset((page - 1) * page_size).limit(page_size).all()
    return page_success([BookingOut.from_orm(b) for b in items], total, page, page_size)


@router.post("/bookings")
def create_booking(
    req: BookingCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """预约会议室（含时间冲突检测）

    冲突检测：新预约 [newStart, newEnd) 与已有"已预约"记录重叠则拒绝。
    重叠条件：newStart < existEnd AND newEnd > existStart
    相邻时段不算冲突（如 [9,10) 和 [10,11) 可同时预约）。
    """
    # 基础校验：结束必须晚于开始
    if req.end_time <= req.start_time:
        raise BizException(20032, "结束时间必须晚于开始时间")

    # 会议室必须存在且可用
    room = db.query(MeetingRoom).filter(MeetingRoom.id == req.room_id).first()
    if not room:
        raise BizException(20030, "会议室不存在")
    if room.status != 1:
        raise BizException(20033, "该会议室已停用")

    # 冲突检测：查同一会议室、已预约状态、时间区间重叠的记录
    conflict = db.query(Booking).filter(
        Booking.room_id == req.room_id,
        Booking.status == BOOKING_ACTIVE,
        # newStart < existEnd  且  newEnd > existStart → 重叠
        Booking.start_time < req.end_time,
        Booking.end_time > req.start_time,
    ).first()

    if conflict:
        raise BizException(
            20034,
            f"该时段已被预约（{conflict.start_time} ~ {conflict.end_time}）",
        )

    # 创建预约
    booking = Booking(
        room_id=req.room_id,
        user_id=current_user.id,
        title=req.title,
        start_time=req.start_time,
        end_time=req.end_time,
        status=BOOKING_ACTIVE,
    )
    db.add(booking)
    db.commit()
    db.refresh(booking)
    return success(BookingOut.from_orm(booking))


@router.delete("/bookings/{booking_id}")
def cancel_booking(
    booking_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """取消预约

    取消后时段释放，后续预约不再与之冲突。
    仅预约人或超级管理员可取消；只能取消"已预约"状态的记录。
    """
    booking = db.query(Booking).filter(Booking.id == booking_id).first()
    if not booking:
        raise BizException(20035, "预约记录不存在")
    if booking.status != BOOKING_ACTIVE:
        raise BizException(20036, "该预约已取消，无需重复操作")
    if booking.user_id != current_user.id and not current_user.is_superuser:
        raise BizException(20037, "仅预约人可取消")

    booking.status = BOOKING_CANCELLED
    db.commit()
    return success()
