"""FastAPI 应用入口

启动顺序：
1. 读取配置（settings）
2. 注册中间件（CORS）
3. 挂载静态资源目录（上传文件）
4. 注册全局异常处理器
5. 挂载业务路由

访问 http://localhost:8000/docs 可查看 Swagger 自动生成的接口文档。
"""
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.core.config import settings
from app.core.exceptions import register_exception_handlers
from app.core.logging import setup_logging
from app.api.v1 import router as api_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期钩子

    启动时初始化日志配置，关闭时无额外操作。
    后续如需连接池预热、缓存预热等，可在此处添加。
    """
    setup_logging()
    yield


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
    """健康检查接口，供 Docker / K8s 探活使用"""
    return {"status": "ok"}


if __name__ == "__main__":
    # 本地开发启动命令：python -m app.main
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
