"""AI 服务配置

无 GPU 约束下的模型选型：
- 大模型：Qwen2.5-7B Q4 量化（约5GB内存），CPU 可跑，中文效果好
- 向量模型：bge-small-zh，轻量中文向量模型
- 人脸：InsightFace buffalo_l，千人底库毫秒级比对
- 图像识别：YOLOv8n（nano版），CPU 单帧 0.3-0.6 秒
"""
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        case_sensitive=True,
        extra="ignore",
    )

    PROJECT_NAME: str = "智慧园区 AI 服务"
    API_V1_PREFIX: str = "/api/v1"

    # 模型文件存放目录
    MODELS_DIR: str = "app/models"

    # ===== Ollama 本地大模型 =====
    OLLAMA_BASE_URL: str = "http://localhost:11434"
    # Q4 量化版，CPU 可运行；内存紧张可降级 qwen2.5:3b
    OLLAMA_MODEL: str = "qwen2.5:7b-instruct-q4_0"

    # ===== 向量模型（文档向量化） =====
    EMBEDDING_MODEL: str = "bge-small-zh"

    # ===== 向量库（复用业务 PostgreSQL 的 pgvector 扩展）=====
    # 必须通过环境变量提供，不硬编码密码
    VECTOR_DB_URL: str

    # ===== 人脸核验 =====
    FACE_MODEL: str = "buffalo_l"
    # 相似度阈值，超过判定为同一人
    FACE_THRESHOLD: float = 0.6

    # ===== 图像识别 =====
    YOLO_MODEL: str = "yolov8n.pt"


settings = Settings()
