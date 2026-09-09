"""审批流程 API

对应 P3 任务：请假审批（多级流转、状态机）。

接口清单：
- GET    /approval-templates       审批模板列表
- POST   /approval-templates       新建审批模板
- PUT    /approval-templates/{id}  修改模板
- POST   /approvals                发起审批申请
- GET    /approvals/my             我的申请列表
- GET    /approvals/{id}            审批详情（含流转记录）
- GET    /approvals/todo           待我审批列表
- POST   /approvals/{id}/approve   审批通过（流转到下一节点）
- POST   /approvals/{id}/reject     审批驳回（实例结束）
- POST   /approvals/{id}/withdraw  撤回申请

错误码段：20010-20029（审批相关）。
权限码：oa:approval:{list/add/edit}。
"""
from typing import List

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.dependencies import get_current_user, require_permissions
from app.core.exceptions import BizException
from app.core.response import page_success, success
from app.models.approval import (
    ApprovalInstance,
    ApprovalRecord,
    ApprovalTask,
    ApprovalTemplate,
)
from app.models.role import Role, sys_user_role
from app.models.user import User
from app.schemas.approval import (
    ApproveAction,
    InstanceCreate,
    InstanceDetailOut,
    InstanceOut,
    RecordOut,
    TaskOut,
    TemplateCreate,
    TemplateOut,
)

router = APIRouter(tags=["审批流程"])

# ===== 状态枚举（实例） =====
INSTANCE_PENDING = 0   # 待审批
INSTANCE_APPROVING = 1  # 审批中
INSTANCE_PASSED = 2     # 已通过
INSTANCE_REJECTED = 3   # 已驳回
INSTANCE_WITHDRAWN = 4  # 已撤回

# ===== 操作枚举（流转记录） =====
ACTION_PASS = 1      # 通过
ACTION_REJECT = 2    # 驳回
ACTION_WITHDRAW = 3  # 撤回

# ===== 任务枚举 =====
TASK_PENDING = 0   # 待处理
TASK_PASSED = 1    # 已通过
TASK_REJECTED = 2  # 已驳回


# ====================================================================
# 审批模板
# ====================================================================
@router.get("/approval-templates")
def list_templates(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permissions(["oa:approval:list"])),
):
    """审批模板列表"""
    items = db.query(ApprovalTemplate).order_by(ApprovalTemplate.id.desc()).all()
    return success([TemplateOut.from_orm(t) for t in items])


@router.post("/approval-templates")
def create_template(
    req: TemplateCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permissions(["oa:approval:add"])),
):
    """新建审批模板

    node_config 必须按 order 升序排列，至少 1 个节点。
    """
    if not req.node_config:
        raise BizException(20010, "审批节点不能为空")
    # 校验节点顺序
    orders = [n.get("order") for n in req.node_config]
    if orders != list(range(1, len(orders) + 1)):
        raise BizException(20010, "节点 order 必须从 1 连续递增")

    template = ApprovalTemplate(
        name=req.name,
        type=req.type,
        node_config=req.node_config,
        status=req.status,
    )
    db.add(template)
    db.commit()
    db.refresh(template)
    return success(TemplateOut.from_orm(template))


@router.put("/approval-templates/{template_id}")
def update_template(
    template_id: int,
    req: TemplateCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permissions(["oa:approval:edit"])),
):
    """修改审批模板"""
    template = db.query(ApprovalTemplate).filter(ApprovalTemplate.id == template_id).first()
    if not template:
        raise BizException(20011, "审批模板不存在")

    if req.node_config:
        orders = [n.get("order") for n in req.node_config]
        if orders != list(range(1, len(orders) + 1)):
            raise BizException(20010, "节点 order 必须从 1 连续递增")

    template.name = req.name
    template.type = req.type
    template.node_config = req.node_config
    template.status = req.status
    db.commit()
    db.refresh(template)
    return success(TemplateOut.from_orm(template))


@router.delete("/approval-templates/{template_id}")
def delete_template(
    template_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permissions(["oa:approval:edit"])),
):
    """删除审批模板

    已有审批实例引用的模板不允许删除（保护历史审批记录的 template_id 关联），
    如需停用请将 status 置为 0。
    """
    template = db.query(ApprovalTemplate).filter(ApprovalTemplate.id == template_id).first()
    if not template:
        raise BizException(20011, "审批模板不存在")

    in_use = (
        db.query(ApprovalInstance)
        .filter(ApprovalInstance.template_id == template_id)
        .count()
    )
    if in_use > 0:
        raise BizException(20017, "该模板已存在审批记录，不能删除（可改为停用）")

    db.delete(template)
    db.commit()
    return success()


# ====================================================================
# 审批实例（发起申请、我的申请、详情）
# ====================================================================
@router.post("/approvals")
def create_instance(
    req: InstanceCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """发起审批申请

    逻辑：
    1. 查模板，校验启用状态
    2. 取第 1 节点的 role_id，找到对应角色用户作为首节点审批人
    3. 创建 instance(status=PENDING, current_node=1)
    4. 创建首节点 task(approver=首节点审批人)
    """
    template = db.query(ApprovalTemplate).filter(
        ApprovalTemplate.id == req.template_id,
        ApprovalTemplate.status == 1,
    ).first()
    if not template:
        raise BizException(20011, "审批模板不存在或已停用")

    nodes = template.node_config or []
    if not nodes:
        raise BizException(20010, "模板未配置审批节点")

    # 取第 1 节点
    first_node = next((n for n in nodes if n.get("order") == 1), None)
    if not first_node:
        raise BizException(20010, "首节点配置错误")

    # 找首节点角色对应的用户（取该角色的第一个用户作为审批人）
    approver = (
        db.query(User)
        .join(sys_user_role, User.id == sys_user_role.c.user_id)
        .join(Role, Role.id == sys_user_role.c.role_id)
        .filter(Role.id == first_node["role_id"], User.status == 1)
        .first()
    )
    if not approver:
        raise BizException(20012, f"节点1未找到可审批人(角色ID={first_node['role_id']})")

    # 创建实例
    instance = ApprovalInstance(
        template_id=req.template_id,
        applicant_id=current_user.id,
        title=req.title,
        form_data=req.form_data,
        status=INSTANCE_PENDING,
        current_node=1,
    )
    db.add(instance)
    db.flush()  # 拿到 instance.id

    # 创建首节点待办
    task = ApprovalTask(
        instance_id=instance.id,
        approver_id=approver.id,
        node_index=1,
        status=TASK_PENDING,
    )
    db.add(task)
    db.commit()
    db.refresh(instance)
    return success(InstanceOut.from_orm(instance))


@router.get("/approvals/my")
def list_my_instances(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    status: int = Query(None, description="状态筛选"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """我的申请列表"""
    query = db.query(ApprovalInstance).filter(ApprovalInstance.applicant_id == current_user.id)
    if status is not None:
        query = query.filter(ApprovalInstance.status == status)
    query = query.order_by(ApprovalInstance.id.desc())
    total = query.count()
    items = query.offset((page - 1) * page_size).limit(page_size).all()
    return page_success([InstanceOut.from_orm(i) for i in items], total, page, page_size)


@router.get("/approvals/todo")
def list_todo(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """待我审批列表（只返回 status=0 待处理任务）

    注意：本路由必须注册在 /approvals/{instance_id} 之前，
    否则 /todo 会被 {instance_id} 抢先匹配，"todo" 无法转 int → 422。
    """
    query = db.query(ApprovalTask).filter(
        ApprovalTask.approver_id == current_user.id,
        ApprovalTask.status == TASK_PENDING,
    ).order_by(ApprovalTask.id.desc())
    total = query.count()
    items = query.offset((page - 1) * page_size).limit(page_size).all()
    return page_success([TaskOut.from_orm(t) for t in items], total, page, page_size)


@router.get("/approvals/{instance_id}")
def get_instance(
    instance_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """审批详情（含流转记录）"""
    instance = db.query(ApprovalInstance).filter(ApprovalInstance.id == instance_id).first()
    if not instance:
        raise BizException(20013, "审批实例不存在")

    records = db.query(ApprovalRecord).filter(
        ApprovalRecord.instance_id == instance_id
    ).order_by(ApprovalRecord.node_index, ApprovalRecord.id).all()

    return success(InstanceDetailOut(
        instance=InstanceOut.from_orm(instance),
        records=[RecordOut.from_orm(r) for r in records],
    ).dict())


# ====================================================================
# 待办与审批操作
# ====================================================================
@router.post("/approvals/{instance_id}/approve")
def approve(
    instance_id: int,
    req: ApproveAction,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """审批通过

    流转逻辑：
    1. 校验当前用户是否有该实例的待处理任务
    2. 标记当前 task=已通过，写流转记录(action=通过)
    3. 若非末节点 → 推进 current_node+1，建下一节点 task
    4. 若是末节点 → instance.status=已通过
    """
    instance = db.query(ApprovalInstance).filter(ApprovalInstance.id == instance_id).first()
    if not instance:
        raise BizException(20013, "审批实例不存在")
    if instance.status not in (INSTANCE_PENDING, INSTANCE_APPROVING):
        raise BizException(20014, "该申请已结束，无法审批")

    # 找当前用户在该实例的待处理任务
    task = db.query(ApprovalTask).filter(
        ApprovalTask.instance_id == instance_id,
        ApprovalTask.approver_id == current_user.id,
        ApprovalTask.status == TASK_PENDING,
    ).first()
    if not task:
        raise BizException(20015, "无待处理任务或您无权审批")

    # 标记任务通过
    task.status = TASK_PASSED
    # 实例进入审批中
    instance.status = INSTANCE_APPROVING

    # 写流转记录
    db.add(ApprovalRecord(
        instance_id=instance_id,
        node_index=task.node_index,
        approver_id=current_user.id,
        action=ACTION_PASS,
        comment=req.comment,
    ))

    # 判断是否末节点
    template = instance.template
    nodes = template.node_config or []
    max_order = max((n.get("order", 0) for n in nodes), default=0)

    if task.node_index >= max_order:
        # 末节点通过 → 实例通过
        instance.status = INSTANCE_PASSED
    else:
        # 推进到下一节点
        next_order = task.node_index + 1
        next_node = next((n for n in nodes if n.get("order") == next_order), None)
        if not next_node:
            raise BizException(20010, f"节点{next_order}配置错误")
        next_approver = (
            db.query(User)
            .join(sys_user_role, User.id == sys_user_role.c.user_id)
            .join(Role, Role.id == sys_user_role.c.role_id)
            .filter(Role.id == next_node["role_id"], User.status == 1)
            .first()
        )
        if not next_approver:
            raise BizException(20012, f"节点{next_order}未找到可审批人")
        instance.current_node = next_order
        db.add(ApprovalTask(
            instance_id=instance_id,
            approver_id=next_approver.id,
            node_index=next_order,
            status=TASK_PENDING,
        ))

    db.commit()
    return success()


@router.post("/approvals/{instance_id}/reject")
def reject(
    instance_id: int,
    req: ApproveAction,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """审批驳回（实例直接结束）"""
    instance = db.query(ApprovalInstance).filter(ApprovalInstance.id == instance_id).first()
    if not instance:
        raise BizException(20013, "审批实例不存在")
    if instance.status not in (INSTANCE_PENDING, INSTANCE_APPROVING):
        raise BizException(20014, "该申请已结束，无法审批")

    task = db.query(ApprovalTask).filter(
        ApprovalTask.instance_id == instance_id,
        ApprovalTask.approver_id == current_user.id,
        ApprovalTask.status == TASK_PENDING,
    ).first()
    if not task:
        raise BizException(20015, "无待处理任务或您无权审批")

    # 标记任务驳回
    task.status = TASK_REJECTED
    # 实例驳回（结束）
    instance.status = INSTANCE_REJECTED

    # 写流转记录
    db.add(ApprovalRecord(
        instance_id=instance_id,
        node_index=task.node_index,
        approver_id=current_user.id,
        action=ACTION_REJECT,
        comment=req.comment,
    ))

    db.commit()
    return success()


@router.post("/approvals/{instance_id}/withdraw")
def withdraw(
    instance_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """撤回申请

    仅申请人本人可撤回，且仅 PENDING/APPROVING 态可撤回。
    """
    instance = db.query(ApprovalInstance).filter(ApprovalInstance.id == instance_id).first()
    if not instance:
        raise BizException(20013, "审批实例不存在")
    if instance.applicant_id != current_user.id:
        raise BizException(20016, "仅申请人可撤回")
    if instance.status not in (INSTANCE_PENDING, INSTANCE_APPROVING):
        raise BizException(20014, "该申请已结束，无法撤回")

    # 撤回当前待处理任务
    pending_tasks = db.query(ApprovalTask).filter(
        ApprovalTask.instance_id == instance_id,
        ApprovalTask.status == TASK_PENDING,
    ).all()
    for t in pending_tasks:
        t.status = TASK_REJECTED

    instance.status = INSTANCE_WITHDRAWN
    db.add(ApprovalRecord(
        instance_id=instance_id,
        node_index=instance.current_node,
        approver_id=current_user.id,
        action=ACTION_WITHDRAW,
        comment="申请人撤回",
    ))

    db.commit()
    return success()
