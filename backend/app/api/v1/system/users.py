"""用户管理 API"""
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.dependencies import get_current_user, require_permissions
from app.core.exceptions import BizException
from app.core.response import page_success, success
from app.core.security import hash_password
from app.models.role import Role
from app.models.user import User
from app.schemas.user import UserCreate, UserUpdate, UserOut

router = APIRouter(prefix="/users", tags=["用户管理"])


@router.get("")
def list_users(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    username: str = Query(None),
    dept_id: int = Query(None),
    status: int = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permissions(["system:user:list"])),
):
    """用户列表"""
    query = db.query(User)
    if username:
        query = query.filter(User.username.contains(username))
    if dept_id:
        query = query.filter(User.dept_id == dept_id)
    if status is not None:
        query = query.filter(User.status == status)

    total = query.count()
    items = query.offset((page - 1) * page_size).limit(page_size).all()
    return page_success([UserOut.from_orm(u) for u in items], total, page, page_size)


@router.post("")
def create_user(
    req: UserCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permissions(["system:user:add"])),
):
    """新增用户"""
    if db.query(User).filter(User.username == req.username).first():
        raise BizException(12002, "用户名已存在")

    user = User(
        username=req.username,
        password=hash_password(req.password),
        nickname=req.nickname,
        phone=req.phone,
        email=req.email,
        dept_id=req.dept_id,
        status=req.status,
    )
    if req.role_ids:
        user.roles = db.query(Role).filter(Role.id.in_(req.role_ids)).all()

    db.add(user)
    db.commit()
    return success(UserOut.from_orm(user))


@router.put("/{user_id}")
def update_user(
    user_id: int,
    req: UserUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permissions(["system:user:edit"])),
):
    """修改用户"""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise BizException(12001, "用户不存在")

    data = req.dict(exclude_unset=True)
    role_ids = data.pop("role_ids", None)
    for k, v in data.items():
        setattr(user, k, v)

    if role_ids is not None:
        user.roles = db.query(Role).filter(Role.id.in_(role_ids)).all() if role_ids else []

    db.commit()
    return success(UserOut.from_orm(user))


@router.delete("/{user_id}")
def delete_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permissions(["system:user:delete"])),
):
    """删除用户"""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise BizException(12001, "用户不存在")
    db.delete(user)
    db.commit()
    return success()


@router.put("/{user_id}/password")
def reset_password(
    user_id: int,
    password: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permissions(["system:user:reset-pwd"])),
):
    """重置密码"""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise BizException(12001, "用户不存在")
    user.password = hash_password(password)
    db.commit()
    return success()


@router.put("/{user_id}/status")
def toggle_status(
    user_id: int,
    status: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permissions(["system:user:edit"])),
):
    """启用/禁用用户"""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise BizException(12001, "用户不存在")
    user.status = status
    db.commit()
    return success()
