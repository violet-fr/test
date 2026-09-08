"""用户模型"""
from sqlalchemy import Column, String, Integer, Boolean, ForeignKey
from sqlalchemy.orm import relationship

from app.models.base import BaseModel

user_role = None  # 延迟引用，见下方


class User(BaseModel):
    __tablename__ = "sys_user"

    username = Column(String(64), unique=True, index=True, nullable=False, comment="用户名")
    password = Column(String(255), nullable=False, comment="密码")
    nickname = Column(String(64), comment="昵称")
    phone = Column(String(20), comment="手机号")
    email = Column(String(128), comment="邮箱")
    avatar = Column(String(255), comment="头像")
    dept_id = Column(Integer, ForeignKey("sys_dept.id"), comment="部门ID")
    status = Column(Integer, default=1, comment="状态 1启用 0禁用")
    is_superuser = Column(Boolean, default=False, comment="超级管理员")

    dept = relationship("Dept", back_populates="users")
    roles = relationship("Role", secondary="sys_user_role", back_populates="users")
