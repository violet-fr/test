"""部门模型"""
from sqlalchemy import Column, String, Integer
from sqlalchemy.orm import relationship

from app.models.base import BaseModel


class Dept(BaseModel):
    __tablename__ = "sys_dept"

    parent_id = Column(Integer, default=0, comment="父部门ID")
    name = Column(String(64), nullable=False, comment="部门名称")
    sort = Column(Integer, default=0, comment="排序")
    status = Column(Integer, default=1, comment="状态")

    users = relationship("User", back_populates="dept")
