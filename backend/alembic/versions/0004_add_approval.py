"""新增审批流程四张表

对应 P3 任务：请假审批（多级流转、状态机）。
- biz_approval_template  审批模板（定义流程节点序列）
- biz_approval_instance  审批实例（一条申请）
- biz_approval_record     流转记录（每次操作留痕）
- biz_approval_task       待办任务（当前待谁审批）

Revision ID: 0004_add_approval
Revises: 0003_add_notice_read
Create Date: 2026-09-09
"""
from alembic import op
import sqlalchemy as sa

# revision identifiers
revision = "0004_add_approval"
down_revision = "0003_add_notice_read"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ===== 审批模板 =====
    op.create_table(
        "biz_approval_template",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("name", sa.String(length=100), nullable=False, comment="模板名称"),
        sa.Column("type", sa.String(length=50), nullable=False, comment="类型 leave/reimburse/business"),
        sa.Column("node_config", sa.JSON(), nullable=True, comment="节点配置JSON"),
        sa.Column("status", sa.Integer(), nullable=True, comment="状态 1启用 0停用"),
        sa.Column("created_at", sa.DateTime(), server_default=sa.text("now()"), nullable=True),
        sa.Column("updated_at", sa.DateTime(), server_default=sa.text("now()"), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )

    # ===== 审批实例 =====
    op.create_table(
        "biz_approval_instance",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("template_id", sa.Integer(), nullable=False, comment="模板ID"),
        sa.Column("applicant_id", sa.Integer(), nullable=False, comment="申请人ID"),
        sa.Column("title", sa.String(length=200), nullable=False, comment="申请标题"),
        sa.Column("form_data", sa.JSON(), nullable=True, comment="表单数据"),
        sa.Column("status", sa.Integer(), nullable=True, comment="状态 0待审批 1审批中 2通过 3驳回 4撤回"),
        sa.Column("current_node", sa.Integer(), nullable=True, comment="当前节点序号"),
        sa.Column("created_at", sa.DateTime(), server_default=sa.text("now()"), nullable=True),
        sa.Column("updated_at", sa.DateTime(), server_default=sa.text("now()"), nullable=True),
        sa.ForeignKeyConstraint(["template_id"], ["biz_approval_template.id"]),
        sa.ForeignKeyConstraint(["applicant_id"], ["sys_user.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_biz_approval_instance_template_id", "biz_approval_instance", ["template_id"], unique=False)
    op.create_index("ix_biz_approval_instance_applicant_id", "biz_approval_instance", ["applicant_id"], unique=False)

    # ===== 流转记录 =====
    op.create_table(
        "biz_approval_record",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("instance_id", sa.Integer(), nullable=False, comment="实例ID"),
        sa.Column("node_index", sa.Integer(), nullable=False, comment="第几个节点"),
        sa.Column("approver_id", sa.Integer(), nullable=False, comment="审批人ID"),
        sa.Column("action", sa.Integer(), nullable=False, comment="操作 1通过 2驳回 3撤回"),
        sa.Column("comment", sa.String(length=500), nullable=True, comment="审批意见"),
        sa.Column("created_at", sa.DateTime(), server_default=sa.text("now()"), nullable=True),
        sa.Column("updated_at", sa.DateTime(), server_default=sa.text("now()"), nullable=True),
        sa.ForeignKeyConstraint(["instance_id"], ["biz_approval_instance.id"]),
        sa.ForeignKeyConstraint(["approver_id"], ["sys_user.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_biz_approval_record_instance_id", "biz_approval_record", ["instance_id"], unique=False)

    # ===== 待办任务 =====
    op.create_table(
        "biz_approval_task",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("instance_id", sa.Integer(), nullable=False, comment="实例ID"),
        sa.Column("approver_id", sa.Integer(), nullable=False, comment="审批人ID"),
        sa.Column("node_index", sa.Integer(), nullable=False, comment="节点序号"),
        sa.Column("status", sa.Integer(), nullable=True, comment="状态 0待处理 1已通过 2已驳回"),
        sa.Column("created_at", sa.DateTime(), server_default=sa.text("now()"), nullable=True),
        sa.Column("updated_at", sa.DateTime(), server_default=sa.text("now()"), nullable=True),
        sa.ForeignKeyConstraint(["instance_id"], ["biz_approval_instance.id"]),
        sa.ForeignKeyConstraint(["approver_id"], ["sys_user.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_biz_approval_task_instance_id", "biz_approval_task", ["instance_id"], unique=False)
    op.create_index("ix_biz_approval_task_approver_id", "biz_approval_task", ["approver_id"], unique=False)


def downgrade() -> None:
    op.drop_index("ix_biz_approval_task_approver_id", table_name="biz_approval_task")
    op.drop_index("ix_biz_approval_task_instance_id", table_name="biz_approval_task")
    op.drop_table("biz_approval_task")
    op.drop_index("ix_biz_approval_record_instance_id", table_name="biz_approval_record")
    op.drop_table("biz_approval_record")
    op.drop_index("ix_biz_approval_instance_applicant_id", table_name="biz_approval_instance")
    op.drop_index("ix_biz_approval_instance_template_id", table_name="biz_approval_instance")
    op.drop_table("biz_approval_instance")
    op.drop_table("biz_approval_template")
