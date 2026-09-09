"""会议室预约模型

对应 P3 任务：会议室预约（冲突检测）。

两表关系：
- meeting_room   会议室档案
- booking        预约记录（关联会议室和预约人）

冲突检测算法：
  新预约 [newStart, newEnd) 与已有预约重叠的条件：
  newStart < existEnd AND newEnd > existStart
  （区间半开，相邻时段不冲突，例如 [9,10) 与 [10,11) 不冲突）
"""
from sqlalchemy import Column, String, Integer, DateTime, ForeignKey

from app.models.base import BaseModel


class MeetingRoom(BaseModel):
    """会议室档案"""
    __tablename__ = "biz_meeting_room"

    name = Column(String(100), nullable=False, comment="会议室名称")
    location = Column(String(200), comment="位置")
    capacity = Column(Integer, comment="容纳人数")
    equipment = Column(String(500), comment="设备配置")
    status = Column(Integer, default=1, comment="状态 1可用 0停用")


class Booking(BaseModel):
    """会议室预约记录"""
    __tablename__ = "biz_booking"

    room_id = Column(Integer, ForeignKey("biz_meeting_room.id"), nullable=False, index=True, comment="会议室ID")
    user_id = Column(Integer, ForeignKey("sys_user.id"), nullable=False, index=True, comment="预约人ID")
    title = Column(String(200), nullable=False, comment="会议主题")
    start_time = Column(DateTime, nullable=False, comment="开始时间")
    end_time = Column(DateTime, nullable=False, comment="结束时间")
    # 状态：1 已预约 / 2 已取消（取消后时段释放，不参与冲突检测）
    status = Column(Integer, default=1, comment="状态 1已预约 2已取消")
