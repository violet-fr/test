"""ORM 基类：通用字段"""
from datetime import datetime

from sqlalchemy import Column, Integer, DateTime, func

from app.core.database import Base


class BaseModel(Base):
    """含 id、创建时间、更新时间的基类"""
    __abstract__ = True

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    created_at = Column(DateTime, server_default=func.now(), comment="创建时间")
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now(), comment="更新时间")
