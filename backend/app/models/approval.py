"""审批流程模型

对应 P3 任务：请假审批（多级流转、状态机）。

四表关系：
- approval_template     审批模板（定义流程节点序列）
- approval_instance     审批实例（一条请假/报销申请）
- approval_record       流转记录（每次审批操作留痕）
- approval_task         待办任务（当前待谁审批）

流转逻辑：
- 发起申请：创建 instance(status=PENDING) + 首节点 task(approver=模板第1节点)
- 通过：若非末节点 → 推进 current_node + 建下一节点 task；末节点 → instance.status=PASSED
- 驳回：instance.status=REJECTED，后续节点不再处理
- 撤回：instance.status=WITHDRAWN（仅申请人本人，且仅 PENDING/APPROVING 态可撤回）
"""
from sqlalchemy import Column, String, Integer, Text, DateTime, ForeignKey, JSON, func
from sqlalchemy.orm import relationship

from app.models.base import BaseModel


class ApprovalTemplate(BaseModel):
    """审批模板

    node_config 示例：
    [
      {"order": 1, "role_id": 2, "name": "部门主管"},
      {"order": 2, "role_id": 3, "name": "HR 审批"},
      {"order": 3, "role_id": 1, "name": "总经理"}
    ]
    """
    __tablename__ = "biz_approval_template"

    name = Column(String(100), nullable=False, comment="模板名称:请假/报销/出差")
    type = Column(String(50), nullable=False, comment="类型 leave/reimburse/business")
    # 节点配置 JSON 数组，按 order 顺序流转
    node_config = Column(JSON, comment="节点配置: [{order,role_id,name}]")
    status = Column(Integer, default=1, comment="状态 1启用 0停用")

    # 关联：审批实例
    instances = relationship("ApprovalInstance", back_populates="template")


class ApprovalInstance(BaseModel):
    """审批实例（一条申请）

    status 状态机：
    0 PENDING    待审批（已创建首节点 task）
    1 APPROVING  审批中（首节点已开始处理）
    2 PASSED     已通过（末节点通过）
    3 REJECTED   已驳回（任一节点驳回 → 实例结束）
    4 WITHDRAWN  已撤回（申请人主动撤回）
    """
    __tablename__ = "biz_approval_instance"

    template_id = Column(Integer, ForeignKey("biz_approval_template.id"), nullable=False, index=True, comment="模板ID")
    applicant_id = Column(Integer, ForeignKey("sys_user.id"), nullable=False, index=True, comment="申请人ID")
    title = Column(String(200), nullable=False, comment="申请标题")
    # 表单数据，如请假：{start_date, end_date, days, reason}
    form_data = Column(JSON, comment="表单数据")
    status = Column(Integer, default=0, comment="状态 0待审批 1审批中 2通过 3驳回 4撤回")
    current_node = Column(Integer, default=1, comment="当前节点序号")

    # 关联
    template = relationship("ApprovalTemplate", back_populates="instances")
    records = relationship("ApprovalRecord", back_populates="instance", order_by="ApprovalRecord.node_index")
    tasks = relationship("ApprovalTask", back_populates="instance")


class ApprovalRecord(BaseModel):
    """审批流转记录（每次操作留痕）

    action: 1 通过 2 驳回 3 撤回
    """
    __tablename__ = "biz_approval_record"

    instance_id = Column(Integer, ForeignKey("biz_approval_instance.id"), nullable=False, index=True, comment="实例ID")
    node_index = Column(Integer, nullable=False, comment="第几个节点")
    approver_id = Column(Integer, ForeignKey("sys_user.id"), nullable=False, comment="审批人ID")
    action = Column(Integer, nullable=False, comment="操作 1通过 2驳回 3撤回")
    comment = Column(String(500), comment="审批意见")

    # 关联
    instance = relationship("ApprovalInstance", back_populates="records")


class ApprovalTask(BaseModel):
    """待办任务（当前待谁审批）

    status: 0 待处理 / 1 已通过 / 2 已驳回
    只查 status=0 的任务即为当前待办。
    """
    __tablename__ = "biz_approval_task"

    instance_id = Column(Integer, ForeignKey("biz_approval_instance.id"), nullable=False, index=True, comment="实例ID")
    approver_id = Column(Integer, ForeignKey("sys_user.id"), nullable=False, index=True, comment="审批人ID")
    node_index = Column(Integer, nullable=False, comment="节点序号")
    status = Column(Integer, default=0, comment="状态 0待处理 1已通过 2已驳回")

    # 关联
    instance = relationship("ApprovalInstance", back_populates="tasks")
