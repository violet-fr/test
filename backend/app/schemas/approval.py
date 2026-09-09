"""审批流程 Schema

对应 P3 任务：请假审批（多级流转、状态机）。
- TemplateCreate/Out：审批模板
- InstanceCreate/Out：审批实例
- ApproveAction：审批操作（通过/驳回）
- TaskOut：待办任务
"""
from datetime import datetime
from typing import Any, List, Optional

from pydantic import BaseModel


# ===== 审批模板 =====
class TemplateCreate(BaseModel):
    """新建审批模板"""
    name: str
    type: str                  # leave/reimburse/business
    # 节点配置：[{order, role_id, name}]
    node_config: List[dict]
    status: int = 1


class TemplateOut(BaseModel):
    """审批模板出参"""
    id: int
    name: str
    type: str
    node_config: Optional[List[dict]] = None
    status: int
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True


# ===== 审批实例 =====
class InstanceCreate(BaseModel):
    """发起审批申请"""
    template_id: int
    title: str
    # 表单数据，如 {start_date, end_date, days, reason}
    form_data: dict


class InstanceOut(BaseModel):
    """审批实例出参"""
    id: int
    template_id: int
    applicant_id: int
    title: str
    form_data: Optional[dict] = None
    status: int
    current_node: int
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class RecordOut(BaseModel):
    """流转记录出参"""
    id: int
    instance_id: int
    node_index: int
    approver_id: int
    action: int
    comment: Optional[str] = None
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class InstanceDetailOut(BaseModel):
    """审批详情出参（含流转记录）"""
    instance: InstanceOut
    records: List[RecordOut] = []


# ===== 审批操作 =====
class ApproveAction(BaseModel):
    """审批操作入参（通过/驳回共用）"""
    comment: Optional[str] = None


# ===== 待办任务 =====
class TaskOut(BaseModel):
    """待办任务出参"""
    id: int
    instance_id: int
    approver_id: int
    node_index: int
    status: int
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True
