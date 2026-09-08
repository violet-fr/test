"""认证 API"""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.core.exceptions import BizException
from app.core.response import success
from app.core.security import create_access_token, create_refresh_token, verify_password, decode_token
from app.models.user import User
from app.schemas.auth import LoginRequest, RefreshRequest

router = APIRouter(prefix="/auth", tags=["认证授权"])


@router.post("/login")
def login(req: LoginRequest, db: Session = Depends(get_db)):
    """用户名密码登录"""
    user = db.query(User).filter(User.username == req.username).first()
    if not user or not verify_password(req.password, user.password):
        raise BizException(11001, "用户名或密码错误")
    if user.status != 1:
        raise BizException(12001, "账号已禁用")

    access_token = create_access_token(str(user.id))
    refresh_token = create_refresh_token(str(user.id))

    return success({
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
        "user": {
            "id": user.id,
            "username": user.username,
            "nickname": user.nickname,
            "avatar": user.avatar,
            "roles": [r.code for r in user.roles],
        },
    })


@router.post("/refresh")
def refresh(req: RefreshRequest):
    """刷新 Token"""
    try:
        payload = decode_token(req.refresh_token)
    except Exception:
        raise BizException(11002, "刷新令牌无效或已过期")

    if payload.get("type") != "refresh":
        raise BizException(11002, "令牌类型错误")

    user_id = payload.get("sub")
    access_token = create_access_token(user_id)
    return success({"access_token": access_token, "token_type": "bearer"})


@router.get("/me")
def me(current_user: User = Depends(get_current_user)):
    """获取当前用户信息（需鉴权）"""
    return success({
        "id": current_user.id,
        "username": current_user.username,
        "nickname": current_user.nickname,
        "avatar": current_user.avatar,
        "roles": [r.code for r in current_user.roles],
    })
