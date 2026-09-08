"""初始化基础数据：角色、菜单、部门、管理员、业务示例数据"""
import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from datetime import datetime, timedelta

from app.core.database import SessionLocal
from app.core.security import hash_password
from app.models.user import User
from app.models.role import Role
from app.models.menu import Menu
from app.models.dept import Dept
from app.models.vehicle import Vehicle, ParkingSpot, MonthlyCard
from app.models.notice import Notice

# 管理员密码从环境变量读取，避免硬编码
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD")
if not ADMIN_PASSWORD:
    print("⚠️  警告：未设置 ADMIN_PASSWORD 环境变量，使用开发默认密码。生产环境务必设置！")
    ADMIN_PASSWORD = "dev_admin_pass_change_me"


def init():
    db = SessionLocal()
    try:
        # ===== 部门 =====
        if not db.query(Dept).first():
            root = Dept(name="智慧园区", parent_id=0, sort=1)
            db.add(root)
            db.flush()
            db.add(Dept(name="行政部", parent_id=root.id, sort=1))
            db.add(Dept(name="技术部", parent_id=root.id, sort=2))
            db.add(Dept(name="安保部", parent_id=root.id, sort=3))

        # ===== 菜单 =====
        if not db.query(Menu).first():
            menus = [
                Menu(parent_id=0, name="系统管理", path="/system", component="Layout", icon="setting", sort=1, type=1),
                Menu(parent_id=0, name="办公协同", path="/oa", component="Layout", icon="document", sort=2, type=1),
                Menu(parent_id=0, name="车辆管理", path="/vehicle", component="Layout", icon="car", sort=3, type=1),
                Menu(parent_id=0, name="安防通行", path="/access", component="Layout", icon="lock", sort=4, type=1),
                Menu(parent_id=0, name="设备物联", path="/device", component="Layout", icon="cpu", sort=5, type=1),
                Menu(parent_id=0, name="事件中心", path="/event", component="Layout", icon="bell", sort=6, type=1),
                Menu(parent_id=0, name="报修工单", path="/service", component="Layout", icon="wrench", sort=7, type=1),
            ]
            db.add_all(menus)
            db.flush()

            sys_id = menus[0].id
            db.add_all([
                Menu(parent_id=sys_id, name="用户管理", path="user", component="system/user", permission="system:user:list", sort=1, type=2),
                Menu(parent_id=sys_id, name="角色管理", path="role", component="system/role", permission="system:role:list", sort=2, type=2),
                Menu(parent_id=sys_id, name="菜单管理", path="menu", component="system/menu", permission="system:menu:list", sort=3, type=2),
                Menu(parent_id=sys_id, name="部门管理", path="dept", component="system/dept", permission="system:dept:list", sort=4, type=2),
            ])

        # ===== 角色：admin / employee / visitor =====
        all_menus = db.query(Menu).all()

        admin_role = db.query(Role).filter(Role.code == "admin").first()
        if not admin_role:
            admin_role = Role(name="超级管理员", code="admin", sort=1)
            admin_role.menus = all_menus
            db.add(admin_role)

        # 员工角色：可访问办公协同、车辆、访客等业务模块
        employee_role = db.query(Role).filter(Role.code == "employee").first()
        if not employee_role:
            employee_role = Role(name="园区员工", code="employee", sort=2)
            # 员工可见办公协同、车辆管理、访客管理等菜单（不含系统管理）
            emp_menus = [m for m in all_menus if m.path in ("/oa", "/vehicle", "/access", "/visitor")]
            employee_role.menus = emp_menus
            db.add(employee_role)

        # 访客角色：仅可访问自己的预约、问答等
        visitor_role = db.query(Role).filter(Role.code == "visitor").first()
        if not visitor_role:
            visitor_role = Role(name="访客", code="visitor", sort=3)
            visitor_role.menus = []
            db.add(visitor_role)

        db.flush()

        # ===== 超级管理员 =====
        admin = db.query(User).filter(User.username == "admin").first()
        if not admin:
            admin = User(
                username="admin",
                password=hash_password(ADMIN_PASSWORD),
                nickname="超级管理员",
                is_superuser=True,
                status=1,
            )
            admin.roles = [admin_role]
            db.add(admin)

        # ===== 示例员工 =====
        if not db.query(User).filter(User.username == "employee01").first():
            emp = User(
                username="employee01",
                password=hash_password("emp123456"),
                nickname="张三（员工）",
                phone="13800138001",
                status=1,
            )
            emp.roles = [employee_role]
            db.add(emp)

        # ===== 车位（示例 10 个）=====
        if not db.query(ParkingSpot).first():
            spots = [ParkingSpot(spot_code=f"A-{i:03d}", area="A区", status=0) for i in range(1, 11)]
            db.add_all(spots)

        # ===== 示例车辆 + 月卡 =====
        if not db.query(Vehicle).first():
            emp_user = db.query(User).filter(User.username == "employee01").first()
            if emp_user:
                v = Vehicle(
                    plate_number="京A12345",
                    owner_name="张三",
                    owner_id=emp_user.id,
                    vehicle_type="小型汽车",
                    color="黑色",
                    is_monthly=True,
                    status=1,
                )
                db.add(v)
                db.flush()
                db.add(MonthlyCard(
                    vehicle_id=v.id,
                    plate_number="京A12345",
                    start_date=datetime.now(),
                    end_date=datetime.now() + timedelta(days=365),
                    status=1,
                ))

        # ===== 示例公告 =====
        if not db.query(Notice).first():
            db.add(Notice(
                title="欢迎使用智慧园区综合管理平台",
                content="<p>本平台已上线，包含办公协同、车辆管理、安防通行、AI 智能等功能。</p>",
                type="notice",
                status=1,
                publisher_id=1,
                publish_time=datetime.now(),
            ))

        db.commit()
        print("初始化数据完成：")
        print("  - 角色：admin / employee / visitor")
        print("  - 管理员账号：admin")
        print("  - 示例员工：employee01 / emp123456")
        print("  - 车位 10 个、车辆 1 辆（月卡）、公告 1 条")
    finally:
        db.close()


if __name__ == "__main__":
    init()
