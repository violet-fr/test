"""API v1 路由聚合：各模块在此挂载"""
from fastapi import APIRouter

from app.api.v1 import auth
from app.api.v1.system import router as system_router

router = APIRouter(prefix="/api/v1")

# 认证授权
router.include_router(auth.router)

# 系统管理
router.include_router(system_router)

# 办公协同（P3：通知公告 / 会议室预约 / 审批流程）—— 代码位于 app/modules/oa
from app.modules.oa import router as oa_router  # noqa: E402
router.include_router(oa_router)

# 以下模块由对应小组开发后挂载：
# from app.api.v1.vehicle import router as vehicle_router; router.include_router(vehicle_router)
# from app.api.v1.access import router as access_router; router.include_router(access_router)
# from app.api.v1.visitor import router as visitor_router; router.include_router(visitor_router)
# from app.api.v1.device import router as device_router; router.include_router(device_router)
# from app.api.v1.event import router as event_router; router.include_router(event_router)
# from app.api.v1.service import router as service_router; router.include_router(service_router)
