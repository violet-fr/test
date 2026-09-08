"""ORM 基类模块

所有业务模型继承 BaseModel，自动获得 id / created_at / updated_at 字段，
避免每张表重复定义这些通用字段。
"""
from sqlalchemy import Column, Integer, DateTime, func

from app.core.database import Base


class BaseModel(Base):
    """所有业务表的基类

    __abstract__ = True 表示不创建真实表，仅作为父类被继承。
    子类自动继承以下字段：
    - id: 自增主键
    - created_at: 创建时间，由数据库自动填充
    - updated_at: 更新时间，更新记录时自动刷新
    """
    __abstract__ = True

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    # server_default=func.now() 让数据库层面设置默认值，不受应用时区影响
    created_at = Column(DateTime, server_default=func.now(), comment="创建时间")
    # onupdate=func.now() 使得每次 UPDATE 时自动刷新该字段
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now(), comment="更新时间")
