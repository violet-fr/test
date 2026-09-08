"""认证 API"""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.core.exceptions import BizException
from app.core.response import success
from app.core.security import create_access_token, create_refresh_token, verify_password, decode_token, hash_password
from app.models.user import User
from app.models.role import Role
from app.schemas.auth import LoginRequest, RefreshRequest, RegisterRequest

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


@router.post("/register")
def register(req: RegisterRequest, db: Session = Depends(get_db)):
    """用户注册（员工/访客角色）"""
    # 用户名唯一性校验
    if db.query(User).filter(User.username == req.username).first():
        raise BizException(12002, "用户名已存在")

    # 角色白名单：仅允许注册 employee / visitor，admin 由后台分配
    if req.role_code not in ("employee", "visitor"):
        raise BizException(10001, "非法的注册角色")

    role = db.query(Role).filter(Role.code == req.role_code).first()
    if not role:
        raise BizException(12002, f"角色 {req.role_code} 不存在")

    user = User(
        username=req.username,
        password=hash_password(req.password),
        nickname=req.nickname or req.username,
        phone=req.phone,
        email=req.email,
        status=1,
        roles=[role],
    )
    db.add(user)
    db.commit()
    db.refresh(user)

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
