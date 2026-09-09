"""办公协同模块（P3）

包含三个子模块：
- notices：通知公告发布与已读/未读统计
- approvals：审批流程（多级流转状态机）
- meetings：会议室预约（时间冲突检测）

路由统一在本包聚合为 ``router``，再由 ``app.api.v1`` 挂载到 /api/v1/oa 下。
数据模型见 app/models，请求/响应模型见 app/schemas。
"""
from fastapi import APIRouter

from app.modules.oa import approvals, meetings, notices

router = APIRouter(prefix="/oa", tags=["办公协同"])
router.include_router(notices.router)
router.include_router(approvals.router)
router.include_router(meetings.router)
