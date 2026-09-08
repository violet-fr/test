"""角色管理 API"""
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.dependencies import get_current_user, require_permissions
from app.core.exceptions import BizException
from app.core.response import page_success, success
from app.models.menu import Menu
from app.models.role import Role
from app.models.user import User

router = APIRouter(prefix="/roles", tags=["角色管理"])


@router.get("")
def list_roles(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permissions(["system:role:list"])),
):
    """角色列表"""
    query = db.query(Role)
    total = query.count()
    items = query.offset((page - 1) * page_size).limit(page_size).all()
    return page_success([
        {"id": r.id, "name": r.name, "code": r.code, "status": r.status, "sort": r.sort}
        for r in items
    ], total, page, page_size)


@router.post("")
def create_role(
    name: str,
    code: str,
    sort: int = 0,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permissions(["system:role:add"])),
):
    """新增角色"""
    if db.query(Role).filter(Role.code == code).first():
        raise BizException(12002, "角色编码已存在")
    role = Role(name=name, code=code, sort=sort)
    db.add(role)
    db.commit()
    return success({"id": role.id})


@router.put("/{role_id}/menus")
def assign_menus(
    role_id: int,
    menu_ids: list[int],
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permissions(["system:role:edit"])),
):
    """分配菜单权限"""
    role = db.query(Role).filter(Role.id == role_id).first()
    if not role:
        raise BizException(12002, "角色不存在")
    role.menus = db.query(Menu).filter(Menu.id.in_(menu_ids)).all() if menu_ids else []
    db.commit()
    return success()
