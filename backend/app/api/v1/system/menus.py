"""菜单管理 API"""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.dependencies import get_current_user, require_permissions
from app.core.response import success
from app.models.menu import Menu
from app.models.user import User

router = APIRouter(prefix="/menus", tags=["菜单管理"])


def build_menu_tree(menus: list[Menu]) -> list[dict]:
    """构建菜单树"""
    menu_dict = {m.id: {
        "id": m.id, "parent_id": m.parent_id, "name": m.name,
        "path": m.path, "component": m.component, "icon": m.icon,
        "sort": m.sort, "type": m.type, "permission": m.permission,
        "children": [],
    } for m in menus}

    tree = []
    for m in menus:
        node = menu_dict[m.id]
        if m.parent_id == 0:
            tree.append(node)
        elif m.parent_id in menu_dict:
            menu_dict[m.parent_id]["children"].append(node)
    return tree


@router.get("")
def list_menus(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """菜单树"""
    # 超级管理员返回全部，否则按角色权限返回
    if current_user.is_superuser:
        menus = db.query(Menu).order_by(Menu.sort).all()
    else:
        menu_ids = set()
        for role in current_user.roles:
            for menu in role.menus:
                menu_ids.add(menu.id)
        menus = db.query(Menu).filter(Menu.id.in_(menu_ids)).order_by(Menu.sort).all()

    return success(build_menu_tree(menus))
