"""部门管理 API"""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.core.response import success
from app.models.dept import Dept
from app.models.user import User

router = APIRouter(prefix="/depts", tags=["部门管理"])


def build_dept_tree(depts: list[Dept]) -> list[dict]:
    """构建部门树"""
    dept_dict = {d.id: {
        "id": d.id, "parent_id": d.parent_id, "name": d.name,
        "sort": d.sort, "status": d.status, "children": [],
    } for d in depts}

    tree = []
    for d in depts:
        node = dept_dict[d.id]
        if d.parent_id == 0:
            tree.append(node)
        elif d.parent_id in dept_dict:
            dept_dict[d.parent_id]["children"].append(node)
    return tree


@router.get("")
def list_depts(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """部门树"""
    depts = db.query(Dept).order_by(Dept.sort).all()
    return success(build_dept_tree(depts))


@router.post("")
def create_dept(
    name: str,
    parent_id: int = 0,
    sort: int = 0,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """新增部门"""
    dept = Dept(name=name, parent_id=parent_id, sort=sort)
    db.add(dept)
    db.commit()
    return success({"id": dept.id})
