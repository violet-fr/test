"""AI 服务入口"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings

app = FastAPI(title=settings.PROJECT_NAME, version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# 各能力路由（AI 组实现后挂载）
# from app.rag.router import router as rag_router
# from app.face.router import router as face_router
# from app.vision.router import router as vision_router
# app.include_router(rag_router, prefix=settings.API_V1_PREFIX)
# app.include_router(face_router, prefix=settings.API_V1_PREFIX)
# app.include_router(vision_router, prefix=settings.API_V1_PREFIX)


@app.get("/health")
def health():
    return {"status": "ok", "service": "ai"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8001, reload=True)
