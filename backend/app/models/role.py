"""角色模型 + 用户-角色关联表

RBAC 权限模型的核心：
- 用户(User) <-> 角色(Role)：多对多（通过 sys_user_role）
- 角色(Role) <-> 菜单(Menu)：多对多（通过 sys_role_menu）
权限 = 角色关联的菜单上的 permission 字段
"""
from sqlalchemy import Column, String, Integer, ForeignKey, Table
from sqlalchemy.orm import relationship

from app.models.base import BaseModel

# 用户-角色多对多关联表
sys_user_role = Table(
    "sys_user_role",
    BaseModel.metadata,
    Column("user_id", Integer, ForeignKey("sys_user.id"), primary_key=True),
    Column("role_id", Integer, ForeignKey("sys_role.id"), primary_key=True),
)


class Role(BaseModel):
    """角色

    code 为角色唯一编码（admin/employee/visitor），
    注册接口中限制只能选择 employee/visitor，admin 由后台分配。
    """
    __tablename__ = "sys_role"

    name = Column(String(64), nullable=False, comment="角色名称")
    code = Column(String(64), unique=True, nullable=False, comment="角色编码(admin/employee/visitor)")
    status = Column(Integer, default=1, comment="状态 1启用 0禁用")
    sort = Column(Integer, default=0, comment="排序")

    # 关联：拥有该角色的用户
    users = relationship("User", secondary=sys_user_role, back_populates="roles")
    # 关联：该角色拥有的菜单（决定权限）
    menus = relationship("Menu", secondary="sys_role_menu", back_populates="roles")
