"""初始化基础数据：超级管理员、默认角色、菜单、部门"""
import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.core.database import SessionLocal
from app.core.security import hash_password
from app.models.user import User
from app.models.role import Role
from app.models.menu import Menu
from app.models.dept import Dept

# 管理员密码从环境变量读取，避免硬编码
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD")
if not ADMIN_PASSWORD:
    print("⚠️  警告：未设置 ADMIN_PASSWORD 环境变量，使用开发默认密码。生产环境务必设置！")
    ADMIN_PASSWORD = "dev_admin_pass_change_me"


def init():
    db = SessionLocal()
    try:
        # 部门
        if not db.query(Dept).first():
            root = Dept(name="智慧园区", parent_id=0, sort=1)
            db.add(root)
            db.flush()
            db.add(Dept(name="行政部", parent_id=root.id, sort=1))
            db.add(Dept(name="技术部", parent_id=root.id, sort=2))
            db.add(Dept(name="安保部", parent_id=root.id, sort=3))

        # 菜单
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

            # 系统管理子菜单
            sys_id = menus[0].id
            db.add_all([
                Menu(parent_id=sys_id, name="用户管理", path="user", component="system/user", permission="system:user:list", sort=1, type=2),
                Menu(parent_id=sys_id, name="角色管理", path="role", component="system/role", permission="system:role:list", sort=2, type=2),
                Menu(parent_id=sys_id, name="菜单管理", path="menu", component="system/menu", permission="system:menu:list", sort=3, type=2),
                Menu(parent_id=sys_id, name="部门管理", path="dept", component="system/dept", permission="system:dept:list", sort=4, type=2),
            ])

        # 角色
        admin_role = db.query(Role).filter(Role.code == "admin").first()
        if not admin_role:
            admin_role = Role(name="超级管理员", code="admin", sort=1)
            db.add(admin_role)
            db.flush()
            # 管理员绑定所有菜单
            all_menus = db.query(Menu).all()
            admin_role.menus = all_menus

        # 超级管理员
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

        db.commit()
        print("初始化数据完成：admin 账号已创建")
    finally:
        db.close()


if __name__ == "__main__":
    init()
