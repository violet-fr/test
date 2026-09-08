"""认证相关 Schema"""
from typing import Optional

from pydantic import BaseModel


class LoginRequest(BaseModel):
    username: str
    password: str


class RegisterRequest(BaseModel):
    username: str
    password: str
    nickname: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    # 注册角色：employee 员工 / visitor 访客（管理员由后台分配）
    role_code: str = "visitor"


class LoginResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    user: dict


class RefreshRequest(BaseModel):
    refresh_token: str
