"""通知公告 Schema

对应 P3 任务：公告发布与已读未读统计。
- NoticeCreate/NoticeUpdate：后台管理端入参
- NoticeOut：出参，列表/详情统一使用
- ReadStatOut：已读未读统计出参
"""
from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel


class NoticeCreate(BaseModel):
    """发布公告入参"""
    title: str
    content: Optional[str] = None
    # 类型：notice 通知 / announcement 公告
    type: str = "notice"
    # 状态：0 草稿 / 1 已发布
    status: int = 1


class NoticeUpdate(BaseModel):
    """修改公告入参（部分字段可选）"""
    title: Optional[str] = None
    content: Optional[str] = None
    type: Optional[str] = None
    status: Optional[int] = None


class NoticeOut(BaseModel):
    """公告出参"""
    id: int
    title: str
    content: Optional[str] = None
    type: str
    status: int
    publisher_id: Optional[int] = None
    publish_time: Optional[datetime] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class UnreadUserOut(BaseModel):
    """未读人员信息"""
    id: int
    username: str
    nickname: Optional[str] = None
    dept_id: Optional[int] = None

    class Config:
        from_attributes = True


class ReadStatOut(BaseModel):
    """已读未读统计出参"""
    notice_id: int
    total: int                # 应读总人数（启用用户数）
    read_count: int           # 已读人数
    unread_count: int         # 未读人数
    unread_users: List[UnreadUserOut] = []  # 未读人员列表（仅展示关键信息）
