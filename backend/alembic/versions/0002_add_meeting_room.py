"""新增会议室与预约两表

对应 P3 任务：会议室预约（冲突检测）。
- biz_meeting_room  会议室档案
- biz_booking        预约记录（关联会议室和预约人）

Revision ID: 0002_add_meeting_room
Revises: 0001_init
Create Date: 2026-09-09
"""
from alembic import op
import sqlalchemy as sa

# revision identifiers
revision = "0002_add_meeting_room"
down_revision = "0001_init"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ===== 会议室档案 =====
    op.create_table(
        "biz_meeting_room",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("name", sa.String(length=100), nullable=False, comment="会议室名称"),
        sa.Column("location", sa.String(length=200), nullable=True, comment="位置"),
        sa.Column("capacity", sa.Integer(), nullable=True, comment="容纳人数"),
        sa.Column("equipment", sa.String(length=500), nullable=True, comment="设备配置"),
        sa.Column("status", sa.Integer(), nullable=True, comment="状态 1可用 0停用"),
        sa.Column("created_at", sa.DateTime(), server_default=sa.text("now()"), nullable=True),
        sa.Column("updated_at", sa.DateTime(), server_default=sa.text("now()"), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )

    # ===== 预约记录 =====
    op.create_table(
        "biz_booking",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("room_id", sa.Integer(), nullable=False, comment="会议室ID"),
        sa.Column("user_id", sa.Integer(), nullable=False, comment="预约人ID"),
        sa.Column("title", sa.String(length=200), nullable=False, comment="会议主题"),
        sa.Column("start_time", sa.DateTime(), nullable=False, comment="开始时间"),
        sa.Column("end_time", sa.DateTime(), nullable=False, comment="结束时间"),
        sa.Column("status", sa.Integer(), nullable=True, comment="状态 1已预约 2已取消"),
        sa.Column("created_at", sa.DateTime(), server_default=sa.text("now()"), nullable=True),
        sa.Column("updated_at", sa.DateTime(), server_default=sa.text("now()"), nullable=True),
        sa.ForeignKeyConstraint(["room_id"], ["biz_meeting_room.id"]),
        sa.ForeignKeyConstraint(["user_id"], ["sys_user.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    # 按会议室查预约 + 按时间范围做冲突检测
    op.create_index("ix_biz_booking_room_id", "biz_booking", ["room_id"], unique=False)
    op.create_index("ix_biz_booking_user_id", "biz_booking", ["user_id"], unique=False)
    # 复合索引：加速冲突检测 SQL（room_id + start_time + end_time 联合过滤）
    op.create_index(
        "ix_biz_booking_room_time",
        "biz_booking",
        ["room_id", "start_time", "end_time"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index("ix_biz_booking_room_time", table_name="biz_booking")
    op.drop_index("ix_biz_booking_user_id", table_name="biz_booking")
    op.drop_index("ix_biz_booking_room_id", table_name="biz_booking")
    op.drop_table("biz_booking")
    op.drop_table("biz_meeting_room")
