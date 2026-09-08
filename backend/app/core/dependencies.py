"""公共依赖注入模块

提供 FastAPI 的依赖注入函数，在路由中通过 Depends() 使用：
- get_current_user: 从 Token 解析当前用户
- require_permissions: 基于 RBAC 的权限校验

设计要点：
- 权限校验不依赖 Token 中存储的角色（Token 可能被篡改且角色变更不实时），
  而是每次从数据库查 user -> roles -> menus -> permission，保证权限变更即时生效。
- 超级管理员（is_superuser=True）跳过所有权限校验，便于系统维护。
"""
from typing import List

from fastapi import Depends, Header
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.exceptions import BizException
from app.core.security import decode_token
from app.models.user import User


def get_current_user(
    authorization: str = Header(None),
    db: Session = Depends(get_db),
) -> User:
    """获取当前登录用户

    从 Authorization: Bearer <token> 头中提取并校验 Token，
    返回对应的 User 对象（已校验状态为启用）。

    用法：
        @router.get("/me")
        def me(user: User = Depends(get_current_user)):
            ...

    Raises:
        BizException: Token 缺失/无效/用户被禁用时抛出
    """
    if not authorization or not authorization.startswith("Bearer "):
        raise BizException(10002, "未授权，请先登录")

    token = authorization.replace("Bearer ", "")
    try:
        payload = decode_token(token)
    except Exception:
        raise BizException(11002, "Token 无效或已过期")

    # 防止用 refresh_token 当 access_token 用
    if payload.get("type") != "access":
        raise BizException(11002, "Token 类型错误")

    user_id = int(payload.get("sub"))
    # 同时校验 status=1，禁用用户无法通过鉴权
    user = db.query(User).filter(User.id == user_id, User.status == 1).first()
    if not user:
        raise BizException(12001, "用户不存在或已禁用")

    return user


def require_permissions(permissions: List[str]):
    """权限校验装饰器工厂

    返回一个 FastAPI 依赖函数，校验当前用户是否拥有指定权限中的任意一个。

    用法：
        @router.get("/users")
        def list_users(user: User = Depends(require_permissions(["system:user:list"]))):
            ...

    权限码格式：模块:资源:操作，如 system:user:list / vehicle:vehicle:add

    Args:
        permissions: 允许访问的权限码列表（满足其一即可）

    Returns:
        FastAPI 依赖函数，返回当前用户对象
    """

    def checker(user: User = Depends(get_current_user), db: Session = Depends(get_db)) -> User:
        # 超级管理员拥有所有权限，直接放行
        if user.is_superuser:
            return user

        # 遍历用户的所有角色 -> 角色绑定的菜单 -> 菜单的权限码
        user_perms = set()
        for role in user.roles:
            for menu in role.menus:
                if menu.permission:
                    user_perms.add(menu.permission)

        # 用户权限与所需权限取交集，有交集则放行
        if not any(p in user_perms for p in permissions):
            raise BizException(10003, "无权限访问")

        return user

    return checker
