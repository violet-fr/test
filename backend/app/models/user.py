"""用户模型

系统用户表，支持管理员、员工、访客三种角色（通过关联 sys_role 区分）。
密码字段存储 bcrypt 哈希值，不存明文。
"""
from sqlalchemy import Column, String, Integer, Boolean, ForeignKey
from sqlalchemy.orm import relationship

from app.models.base import BaseModel


class User(BaseModel):
    """系统用户

    角色通过 sys_user_role 关联表实现多对多（一个用户可有多个角色）。
    超级管理员（is_superuser=True）绕过所有权限校验。
    """
    __tablename__ = "sys_user"

    username = Column(String(64), unique=True, index=True, nullable=False, comment="用户名")
    # 存储 bcrypt 哈希（60字符），预留 255 长度
    password = Column(String(255), nullable=False, comment="密码(bcrypt哈希)")
    nickname = Column(String(64), comment="昵称")
    phone = Column(String(20), comment="手机号")
    email = Column(String(128), comment="邮箱")
    avatar = Column(String(255), comment="头像URL")
    dept_id = Column(Integer, ForeignKey("sys_dept.id"), comment="部门ID")
    status = Column(Integer, default=1, comment="状态 1启用 0禁用")
    # 超级管理员标志，为 True 时跳过权限校验
    is_superuser = Column(Boolean, default=False, comment="超级管理员")

    # 关联：所属部门
    dept = relationship("Dept", back_populates="users")
    # 多对多关联：用户角色（通过 sys_user_role 中间表）
    roles = relationship("Role", secondary="sys_user_role", back_populates="users")
