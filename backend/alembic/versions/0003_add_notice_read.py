"""新增公告阅读回执表

对应 P3 任务：公告已读未读统计。
- biz_notice_read  阅读回执（notice_id + user_id 联合唯一）

Revision ID: 0003_add_notice_read
Revises: 0002_add_meeting_room
Create Date: 2026-09-09
"""
from alembic import op
import sqlalchemy as sa

# revision identifiers
revision = "0003_add_notice_read"
down_revision = "0002_add_meeting_room"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "biz_notice_read",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("notice_id", sa.Integer(), nullable=False, comment="公告ID"),
        sa.Column("user_id", sa.Integer(), nullable=False, comment="阅读人ID"),
        sa.Column("read_time", sa.DateTime(), server_default=sa.text("now()"), comment="阅读时间"),
        sa.Column("created_at", sa.DateTime(), server_default=sa.text("now()"), nullable=True),
        sa.Column("updated_at", sa.DateTime(), server_default=sa.text("now()"), nullable=True),
        sa.ForeignKeyConstraint(["notice_id"], ["biz_notice.id"]),
        sa.ForeignKeyConstraint(["user_id"], ["sys_user.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("notice_id", "user_id", name="uk_notice_user"),
    )
    op.create_index("ix_biz_notice_read_notice_id", "biz_notice_read", ["notice_id"], unique=False)
    op.create_index("ix_biz_notice_read_user_id", "biz_notice_read", ["user_id"], unique=False)


def downgrade() -> None:
    op.drop_index("ix_biz_notice_read_user_id", table_name="biz_notice_read")
    op.drop_index("ix_biz_notice_read_notice_id", table_name="biz_notice_read")
    op.drop_table("biz_notice_read")
