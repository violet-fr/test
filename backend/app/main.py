"""FastAPI 应用入口

启动顺序：
1. 读取配置（settings）
2. 初始化日志、Redis 连接
3. 注册中间件（CORS）
4. 挂载静态资源目录（上传文件）
5. 注册全局异常处理器
6. 挂载业务路由

访问 http://localhost:8000/docs 可查看 Swagger 自动生成的接口文档。
"""
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from sqlalchemy import text

from app.core.config import settings
from app.core.database import engine
from app.core.exceptions import register_exception_handlers
from app.core.logging import setup_logging
from app.core.redis import close_redis, get_redis, init_redis
from app.api.v1 import router as api_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期钩子

    启动时：初始化日志、Redis（Redis 失败不阻断启动）。
    关闭时：释放 Redis 连接池。
    """
    setup_logging()
    init_redis()
    yield
    close_redis()


app = FastAPI(
    title=settings.PROJECT_NAME,
    version="1.0.0",
    lifespan=lifespan,
)

# CORS 跨域配置：允许前端域名访问后端 API
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 静态资源：上传的图片通过 /uploads/xxx 直接访问
app.mount("/uploads", StaticFiles(directory=settings.UPLOAD_DIR), name="uploads")

# 注册全局异常处理器，统一错误响应格式
register_exception_handlers(app)

# 挂载 API 路由（/api/v1/...）
app.include_router(api_router)


@app.get("/health")
def health():
    """健康检查接口，供 Docker / K8s 探活与编排使用

    返回各依赖组件的存活状态：
    - status=ok 表示应用进程存活
    - db/redis 字段反映下游依赖连通性（redis 异常不影响整体 status）
    """
    checks = {"status": "ok", "db": "unknown", "redis": "unknown"}

    # 数据库连通性（SQLAlchemy 2.x 原生 SQL 必须用 text() 包裹）
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        checks["db"] = "ok"
    except Exception:
        checks["status"] = "degraded"
        checks["db"] = "error"

    # Redis 连通性（缓存为非核心依赖，不可用时标记 down 但不影响整体存活判定）
    r = get_redis()
    if r is not None:
        try:
            r.ping()
            checks["redis"] = "ok"
        except Exception:
            checks["redis"] = "down"
    else:
        checks["redis"] = "down"

    return checks


if __name__ == "__main__":
    # 本地开发启动命令：python -m app.main
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
