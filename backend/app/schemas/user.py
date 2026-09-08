"""用户相关 Schema"""
from typing import List, Optional

from pydantic import BaseModel


class UserCreate(BaseModel):
    username: str
    password: str
    nickname: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    dept_id: Optional[int] = None
    role_ids: List[int] = []
    status: int = 1


class UserUpdate(BaseModel):
    nickname: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    dept_id: Optional[int] = None
    role_ids: Optional[List[int]] = None
    status: Optional[int] = None


class UserOut(BaseModel):
    id: int
    username: str
    nickname: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    avatar: Optional[str] = None
    dept_id: Optional[int] = None
    status: int

    class Config:
        from_attributes = True
