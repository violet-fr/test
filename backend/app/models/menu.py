"""菜单模型 + 角色菜单关联"""
from sqlalchemy import Column, String, Integer, ForeignKey, Table
from sqlalchemy.orm import relationship

from app.models.base import BaseModel

sys_role_menu = Table(
    "sys_role_menu",
    BaseModel.metadata,
    Column("role_id", Integer, ForeignKey("sys_role.id"), primary_key=True),
    Column("menu_id", Integer, ForeignKey("sys_menu.id"), primary_key=True),
)


class Menu(BaseModel):
    __tablename__ = "sys_menu"

    parent_id = Column(Integer, default=0, comment="父菜单ID")
    name = Column(String(64), nullable=False, comment="菜单名称")
    path = Column(String(255), comment="路由路径")
    component = Column(String(255), comment="组件路径")
    icon = Column(String(64), comment="图标")
    sort = Column(Integer, default=0, comment="排序")
    type = Column(Integer, default=1, comment="类型 1目录 2菜单 3按钮")
    permission = Column(String(128), comment="权限标识")

    roles = relationship("Role", secondary=sys_role_menu, back_populates="menus")
