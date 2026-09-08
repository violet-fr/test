"""公共依赖注入：数据库、当前用户、权限校验"""
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
    """获取当前登录用户"""
    if not authorization or not authorization.startswith("Bearer "):
        raise BizException(10002, "未授权，请先登录")

    token = authorization.replace("Bearer ", "")
    try:
        payload = decode_token(token)
    except Exception:
        raise BizException(11002, "Token 无效或已过期")

    if payload.get("type") != "access":
        raise BizException(11002, "Token 类型错误")

    user_id = int(payload.get("sub"))
    user = db.query(User).filter(User.id == user_id, User.status == 1).first()
    if not user:
        raise BizException(12001, "用户不存在或已禁用")

    return user


def require_permissions(permissions: List[str]):
    """权限校验装饰器工厂：需要拥有指定权限之一"""

    def checker(user: User = Depends(get_current_user), db: Session = Depends(get_db)) -> User:
        # 超级管理员跳过
        if user.is_superuser:
            return user

        # 查询用户所有权限码
        user_perms = set()
        for role in user.roles:
            for menu in role.menus:
                if menu.permission:
                    user_perms.add(menu.permission)

        if not any(p in user_perms for p in permissions):
            raise BizException(10003, "无权限访问")

        return user

    return checker
