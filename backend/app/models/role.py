"""角色模型 + 用户角色关联"""
from sqlalchemy import Column, String, Integer, ForeignKey, Table
from sqlalchemy.orm import relationship

from app.models.base import BaseModel

sys_user_role = Table(
    "sys_user_role",
    BaseModel.metadata,
    Column("user_id", Integer, ForeignKey("sys_user.id"), primary_key=True),
    Column("role_id", Integer, ForeignKey("sys_role.id"), primary_key=True),
)


class Role(BaseModel):
    __tablename__ = "sys_role"

    name = Column(String(64), nullable=False, comment="角色名称")
    code = Column(String(64), unique=True, nullable=False, comment="角色编码")
    status = Column(Integer, default=1, comment="状态")
    sort = Column(Integer, default=0, comment="排序")

    users = relationship("User", secondary=sys_user_role, back_populates="roles")
    menus = relationship("Menu", secondary="sys_role_menu", back_populates="roles")
