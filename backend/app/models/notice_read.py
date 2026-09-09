"""公告阅读回执（已读/未读统计）

P3 任务：公告已读未读统计。
- 一条记录代表"某用户已读某公告"
- 已读人数 = 该 notice_id 的记录数
- 未读人员 = 全部启用用户 - 已读用户
"""
from sqlalchemy import Column, Integer, DateTime, ForeignKey, UniqueConstraint, func

from app.models.base import BaseModel


class NoticeRead(BaseModel):
    """公告阅读回执"""
    __tablename__ = "biz_notice_read"
    __table_args__ = (
        UniqueConstraint("notice_id", "user_id", name="uk_notice_user"),
    )

    notice_id = Column(
        Integer, ForeignKey("biz_notice.id"), nullable=False, index=True, comment="公告ID"
    )
    user_id = Column(
        Integer, ForeignKey("sys_user.id"), nullable=False, index=True, comment="阅读人ID"
    )
    read_time = Column(DateTime, server_default=func.now(), comment="阅读时间")
