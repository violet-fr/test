"""初始化全部表结构（系统域 + 业务域）

Revision ID: 0001_init
Revises:
Create Date: 2026-09-08
"""
from alembic import op
import sqlalchemy as sa
from pgvector.sqlalchemy import Vector

# revision identifiers
revision = "0001_init"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # 启用 pgvector 扩展
    op.execute("CREATE EXTENSION IF NOT EXISTS vector")

    # ===== 系统域 =====
    op.create_table(
        "sys_dept",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("parent_id", sa.Integer(), nullable=True, comment="父部门ID"),
        sa.Column("name", sa.String(length=64), nullable=False, comment="部门名称"),
        sa.Column("sort", sa.Integer(), nullable=True, comment="排序"),
        sa.Column("status", sa.Integer(), nullable=True, comment="状态"),
        sa.Column("created_at", sa.DateTime(), server_default=sa.text("now()"), nullable=True),
        sa.Column("updated_at", sa.DateTime(), server_default=sa.text("now()"), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_table(
        "sys_user",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("username", sa.String(length=64), nullable=False, comment="用户名"),
        sa.Column("password", sa.String(length=255), nullable=False, comment="密码"),
        sa.Column("nickname", sa.String(length=64), nullable=True, comment="昵称"),
        sa.Column("phone", sa.String(length=20), nullable=True, comment="手机号"),
        sa.Column("email", sa.String(length=128), nullable=True, comment="邮箱"),
        sa.Column("avatar", sa.String(length=255), nullable=True, comment="头像"),
        sa.Column("dept_id", sa.Integer(), nullable=True, comment="部门ID"),
        sa.Column("status", sa.Integer(), nullable=True, comment="状态 1启用 0禁用"),
        sa.Column("is_superuser", sa.Boolean(), nullable=True, comment="超级管理员"),
        sa.Column("created_at", sa.DateTime(), server_default=sa.text("now()"), nullable=True),
        sa.Column("updated_at", sa.DateTime(), server_default=sa.text("now()"), nullable=True),
        sa.ForeignKeyConstraint(["dept_id"], ["sys_dept.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_sys_user_username", "sys_user", ["username"], unique=True)

    op.create_table(
        "sys_role",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("name", sa.String(length=64), nullable=False, comment="角色名称"),
        sa.Column("code", sa.String(length=64), nullable=False, comment="角色编码"),
        sa.Column("status", sa.Integer(), nullable=True, comment="状态"),
        sa.Column("sort", sa.Integer(), nullable=True, comment="排序"),
        sa.Column("created_at", sa.DateTime(), server_default=sa.text("now()"), nullable=True),
        sa.Column("updated_at", sa.DateTime(), server_default=sa.text("now()"), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_sys_role_code", "sys_role", ["code"], unique=True)

    op.create_table(
        "sys_menu",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("parent_id", sa.Integer(), nullable=True, comment="父菜单ID"),
        sa.Column("name", sa.String(length=64), nullable=False, comment="菜单名称"),
        sa.Column("path", sa.String(length=255), nullable=True, comment="路由路径"),
        sa.Column("component", sa.String(length=255), nullable=True, comment="组件路径"),
        sa.Column("icon", sa.String(length=64), nullable=True, comment="图标"),
        sa.Column("sort", sa.Integer(), nullable=True, comment="排序"),
        sa.Column("type", sa.Integer(), nullable=True, comment="类型 1目录 2菜单 3按钮"),
        sa.Column("permission", sa.String(length=128), nullable=True, comment="权限标识"),
        sa.Column("created_at", sa.DateTime(), server_default=sa.text("now()"), nullable=True),
        sa.Column("updated_at", sa.DateTime(), server_default=sa.text("now()"), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_table(
        "sys_user_role",
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("role_id", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(["role_id"], ["sys_role.id"]),
        sa.ForeignKeyConstraint(["user_id"], ["sys_user.id"]),
        sa.PrimaryKeyConstraint("user_id", "role_id"),
    )

    op.create_table(
        "sys_role_menu",
        sa.Column("role_id", sa.Integer(), nullable=False),
        sa.Column("menu_id", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(["menu_id"], ["sys_menu.id"]),
        sa.ForeignKeyConstraint(["role_id"], ["sys_role.id"]),
        sa.PrimaryKeyConstraint("role_id", "menu_id"),
    )

    # ===== 车辆域 =====
    op.create_table(
        "biz_vehicle",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("plate_number", sa.String(length=20), nullable=False, comment="车牌号"),
        sa.Column("owner_name", sa.String(length=64), nullable=True, comment="车主姓名"),
        sa.Column("owner_id", sa.Integer(), nullable=True, comment="车主用户ID"),
        sa.Column("vehicle_type", sa.String(length=32), nullable=True, comment="车辆类型"),
        sa.Column("color", sa.String(length=16), nullable=True, comment="颜色"),
        sa.Column("is_monthly", sa.Boolean(), nullable=True, comment="是否月卡车辆"),
        sa.Column("status", sa.Integer(), nullable=True, comment="状态"),
        sa.Column("created_at", sa.DateTime(), server_default=sa.text("now()"), nullable=True),
        sa.Column("updated_at", sa.DateTime(), server_default=sa.text("now()"), nullable=True),
        sa.ForeignKeyConstraint(["owner_id"], ["sys_user.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_biz_vehicle_plate_number", "biz_vehicle", ["plate_number"], unique=True)

    op.create_table(
        "biz_parking_spot",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("spot_code", sa.String(length=32), nullable=False, comment="车位编号"),
        sa.Column("area", sa.String(length=64), nullable=True, comment="区域"),
        sa.Column("status", sa.Integer(), nullable=True, comment="状态 0空闲 1占用 2维护"),
        sa.Column("vehicle_id", sa.Integer(), nullable=True, comment="占用车辆ID"),
        sa.Column("created_at", sa.DateTime(), server_default=sa.text("now()"), nullable=True),
        sa.Column("updated_at", sa.DateTime(), server_default=sa.text("now()"), nullable=True),
        sa.ForeignKeyConstraint(["vehicle_id"], ["biz_vehicle.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_biz_parking_spot_spot_code", "biz_parking_spot", ["spot_code"], unique=True)

    op.create_table(
        "biz_vehicle_access_record",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("plate_number", sa.String(length=20), nullable=False, comment="车牌号"),
        sa.Column("vehicle_id", sa.Integer(), nullable=True, comment="车辆ID"),
        sa.Column("direction", sa.String(length=8), nullable=False, comment="方向"),
        sa.Column("spot_id", sa.Integer(), nullable=True, comment="车位ID"),
        sa.Column("image_url", sa.String(length=255), nullable=True, comment="抓拍图片"),
        sa.Column("access_time", sa.DateTime(), nullable=True, comment="进出时间"),
        sa.Column("created_at", sa.DateTime(), server_default=sa.text("now()"), nullable=True),
        sa.Column("updated_at", sa.DateTime(), server_default=sa.text("now()"), nullable=True),
        sa.ForeignKeyConstraint(["spot_id"], ["biz_parking_spot.id"]),
        sa.ForeignKeyConstraint(["vehicle_id"], ["biz_vehicle.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_biz_vehicle_access_record_plate_number", "biz_vehicle_access_record", ["plate_number"])

    op.create_table(
        "biz_monthly_card",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("vehicle_id", sa.Integer(), nullable=False, comment="车辆ID"),
        sa.Column("plate_number", sa.String(length=20), nullable=True, comment="车牌号"),
        sa.Column("start_date", sa.DateTime(), nullable=True, comment="生效日期"),
        sa.Column("end_date", sa.DateTime(), nullable=True, comment="到期日期"),
        sa.Column("status", sa.Integer(), nullable=True, comment="状态"),
        sa.Column("created_at", sa.DateTime(), server_default=sa.text("now()"), nullable=True),
        sa.Column("updated_at", sa.DateTime(), server_default=sa.text("now()"), nullable=True),
        sa.ForeignKeyConstraint(["vehicle_id"], ["biz_vehicle.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_biz_monthly_card_plate_number", "biz_monthly_card", ["plate_number"])

    # ===== 通行域 =====
    op.create_table(
        "biz_access_person",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=True, comment="关联用户ID"),
        sa.Column("name", sa.String(length=64), nullable=False, comment="姓名"),
        sa.Column("face_feature", Vector(512), nullable=True, comment="人脸特征向量"),
        sa.Column("face_image_url", sa.String(length=255), nullable=True, comment="人脸图片"),
        sa.Column("status", sa.Integer(), nullable=True, comment="状态"),
        sa.Column("created_at", sa.DateTime(), server_default=sa.text("now()"), nullable=True),
        sa.Column("updated_at", sa.DateTime(), server_default=sa.text("now()"), nullable=True),
        sa.ForeignKeyConstraint(["user_id"], ["sys_user.id"]),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_table(
        "biz_verify_record",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("person_id", sa.Integer(), nullable=True, comment="通行人员ID"),
        sa.Column("name", sa.String(length=64), nullable=True, comment="姓名"),
        sa.Column("similarity", sa.Float(), nullable=True, comment="相似度"),
        sa.Column("success", sa.Integer(), nullable=True, comment="是否通过"),
        sa.Column("device_id", sa.String(length=64), nullable=True, comment="设备编号"),
        sa.Column("image_url", sa.String(length=255), nullable=True, comment="核验图片"),
        sa.Column("verified_at", sa.DateTime(), nullable=True, comment="核验时间"),
        sa.Column("created_at", sa.DateTime(), server_default=sa.text("now()"), nullable=True),
        sa.Column("updated_at", sa.DateTime(), server_default=sa.text("now()"), nullable=True),
        sa.ForeignKeyConstraint(["person_id"], ["biz_access_person.id"]),
        sa.PrimaryKeyConstraint("id"),
    )

    # ===== 访客域 =====
    op.create_table(
        "biz_visitor_invitation",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("inviter_id", sa.Integer(), nullable=False, comment="邀请人ID"),
        sa.Column("visitor_name", sa.String(length=64), nullable=False, comment="访客姓名"),
        sa.Column("visitor_phone", sa.String(length=20), nullable=False, comment="访客手机号"),
        sa.Column("visit_date", sa.DateTime(), nullable=False, comment="到访日期"),
        sa.Column("visit_purpose", sa.String(length=255), nullable=True, comment="来访事由"),
        sa.Column("visit_duration", sa.Integer(), nullable=True, comment="预计时长"),
        sa.Column("appointment_code", sa.String(length=64), nullable=True, comment="预约码"),
        sa.Column("status", sa.Integer(), nullable=True, comment="状态"),
        sa.Column("created_at", sa.DateTime(), server_default=sa.text("now()"), nullable=True),
        sa.Column("updated_at", sa.DateTime(), server_default=sa.text("now()"), nullable=True),
        sa.ForeignKeyConstraint(["inviter_id"], ["sys_user.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_biz_visitor_invitation_appointment_code", "biz_visitor_invitation", ["appointment_code"], unique=True)

    op.create_table(
        "biz_visitor_appointment",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("invitation_id", sa.Integer(), nullable=True, comment="关联邀请ID"),
        sa.Column("visitor_name", sa.String(length=64), nullable=False, comment="访客姓名"),
        sa.Column("visitor_phone", sa.String(length=20), nullable=True, comment="访客手机号"),
        sa.Column("visit_date", sa.DateTime(), nullable=True, comment="到访日期"),
        sa.Column("visit_purpose", sa.String(length=255), nullable=True, comment="来访事由"),
        sa.Column("approver_id", sa.Integer(), nullable=True, comment="审批人ID"),
        sa.Column("approve_time", sa.DateTime(), nullable=True, comment="审批时间"),
        sa.Column("status", sa.Integer(), nullable=True, comment="状态"),
        sa.Column("created_at", sa.DateTime(), server_default=sa.text("now()"), nullable=True),
        sa.Column("updated_at", sa.DateTime(), server_default=sa.text("now()"), nullable=True),
        sa.ForeignKeyConstraint(["approver_id"], ["sys_user.id"]),
        sa.ForeignKeyConstraint(["invitation_id"], ["biz_visitor_invitation.id"]),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_table(
        "biz_visit_record",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("appointment_id", sa.Integer(), nullable=True, comment="预约ID"),
        sa.Column("visitor_name", sa.String(length=64), nullable=True, comment="访客姓名"),
        sa.Column("check_in_time", sa.DateTime(), nullable=True, comment="到访时间"),
        sa.Column("check_out_time", sa.DateTime(), nullable=True, comment="离场时间"),
        sa.Column("status", sa.Integer(), nullable=True, comment="状态"),
        sa.Column("created_at", sa.DateTime(), server_default=sa.text("now()"), nullable=True),
        sa.Column("updated_at", sa.DateTime(), server_default=sa.text("now()"), nullable=True),
        sa.ForeignKeyConstraint(["appointment_id"], ["biz_visitor_appointment.id"]),
        sa.PrimaryKeyConstraint("id"),
    )

    # ===== 办公域 =====
    op.create_table(
        "biz_notice",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("title", sa.String(length=255), nullable=False, comment="标题"),
        sa.Column("content", sa.Text(), nullable=True, comment="内容"),
        sa.Column("type", sa.String(length=32), nullable=True, comment="类型"),
        sa.Column("status", sa.Integer(), nullable=True, comment="状态"),
        sa.Column("publisher_id", sa.Integer(), nullable=True, comment="发布人ID"),
        sa.Column("publish_time", sa.DateTime(), nullable=True, comment="发布时间"),
        sa.Column("created_at", sa.DateTime(), server_default=sa.text("now()"), nullable=True),
        sa.Column("updated_at", sa.DateTime(), server_default=sa.text("now()"), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )


def downgrade() -> None:
    op.drop_table("biz_notice")
    op.drop_table("biz_visit_record")
    op.drop_table("biz_visitor_appointment")
    op.drop_table("biz_visitor_invitation")
    op.drop_table("biz_verify_record")
    op.drop_table("biz_access_person")
    op.drop_table("biz_monthly_card")
    op.drop_table("biz_vehicle_access_record")
    op.drop_table("biz_parking_spot")
    op.drop_table("biz_vehicle")
    op.drop_table("sys_role_menu")
    op.drop_table("sys_user_role")
    op.drop_table("sys_menu")
    op.drop_table("sys_role")
    op.drop_table("sys_user")
    op.drop_table("sys_dept")
