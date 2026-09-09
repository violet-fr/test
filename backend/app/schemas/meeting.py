"""会议室预约 Schema

对应 P3 任务：会议室预约（冲突检测）。
"""
from datetime import datetime
from typing import Optional

from pydantic import BaseModel


# ===== 会议室 =====
class RoomCreate(BaseModel):
    """新增会议室"""
    name: str
    location: Optional[str] = None
    capacity: Optional[int] = None
    equipment: Optional[str] = None
    status: int = 1


class RoomUpdate(BaseModel):
    """修改会议室（部分字段可选）"""
    name: Optional[str] = None
    location: Optional[str] = None
    capacity: Optional[int] = None
    equipment: Optional[str] = None
    status: Optional[int] = None


class RoomOut(BaseModel):
    """会议室出参"""
    id: int
    name: str
    location: Optional[str] = None
    capacity: Optional[int] = None
    equipment: Optional[str] = None
    status: int
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


# ===== 预约 =====
class BookingCreate(BaseModel):
    """预约会议室入参"""
    room_id: int
    title: str
    start_time: datetime
    end_time: datetime


class BookingOut(BaseModel):
    """预约出参"""
    id: int
    room_id: int
    user_id: int
    title: str
    start_time: datetime
    end_time: datetime
    status: int
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True
