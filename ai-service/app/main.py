"""AI 服务入口（独立进程，端口 8001）

为什么 AI 服务要独立部署？
1. 依赖重（torch/insightface/ultralytics），与业务后端镜像分离，避免业务镜像过大
2. 发布节奏不同：AI 模型更新频繁，业务后端相对稳定
3. CPU 资源隔离：AI 推理占 CPU，不影响业务接口响应

业务后端通过 HTTP 调用 AI 服务（http://ai-service:8001），AI 服务不直连业务数据库。
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings

app = FastAPI(title=settings.PROJECT_NAME, version="1.0.0")

# AI 服务仅被业务后端调用，CORS 放宽不影响安全（生产环境应限制来源）
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# 各能力路由（AI 组实现后取消注释挂载）
# RAG 智能问答
# from app.rag.router import router as rag_router
# 人脸特征提取/比对
# from app.face.router import router as face_router
# 图像识别（YOLOv8）
# from app.vision.router import router as vision_router
# app.include_router(rag_router, prefix=settings.API_V1_PREFIX)
# app.include_router(face_router, prefix=settings.API_V1_PREFIX)
# app.include_router(vision_router, prefix=settings.API_V1_PREFIX)


@app.get("/health")
def health():
    """健康检查"""
    return {"status": "ok", "service": "ai"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8001, reload=True)
