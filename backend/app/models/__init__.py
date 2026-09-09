"""ORM 模型统一导出（供 Alembic 自动生成迁移）"""
# 系统域
from app.models.base import BaseModel  # noqa
from app.models.user import User  # noqa
from app.models.role import Role, sys_user_role  # noqa
from app.models.menu import Menu, sys_role_menu  # noqa
from app.models.dept import Dept  # noqa

# 车辆域
from app.models.vehicle import Vehicle, ParkingSpot, VehicleAccessRecord, MonthlyCard  # noqa

# 通行域
from app.models.access import AccessPerson, VerifyRecord  # noqa

# 访客域
from app.models.visitor import VisitorInvitation, VisitorAppointment, VisitRecord  # noqa

# 办公域
from app.models.notice import Notice  # noqa
from app.models.notice_read import NoticeRead  # noqa
from app.models.approval import (
    ApprovalTemplate,
    ApprovalInstance,
    ApprovalRecord,
    ApprovalTask,
)  # noqa
from app.models.meeting import MeetingRoom, Booking  # noqa
