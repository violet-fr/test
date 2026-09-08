"""系统管理模块路由聚合"""
from fastapi import APIRouter

from app.api.v1.system import users, roles, menus, depts

router = APIRouter(prefix="/system", tags=["系统管理"])
router.include_router(users.router)
router.include_router(roles.router)
router.include_router(menus.router)
router.include_router(depts.router)
