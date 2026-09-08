"""ORM 模型统一导出（供 Alembic 自动生成迁移）"""
from app.models.base import BaseModel  # noqa
from app.models.user import User  # noqa
from app.models.role import Role, sys_user_role  # noqa
from app.models.menu import Menu, sys_role_menu  # noqa
from app.models.dept import Dept  # noqa
