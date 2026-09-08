"""通知公告"""
from sqlalchemy import Column, String, Integer, Text, DateTime

from app.models.base import BaseModel


class Notice(BaseModel):
    """通知公告"""
    __tablename__ = "biz_notice"

    title = Column(String(255), nullable=False, comment="标题")
    content = Column(Text, comment="内容")
    type = Column(String(32), default="notice", comment="类型 notice通知 announcement公告")
    status = Column(Integer, default=1, comment="状态 0草稿 1已发布")
    publisher_id = Column(Integer, comment="发布人ID")
    publish_time = Column(DateTime, comment="发布时间")
