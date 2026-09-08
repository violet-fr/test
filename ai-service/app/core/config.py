"""AI 服务配置"""
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        case_sensitive=True,
        extra="ignore",
    )

    PROJECT_NAME: str = "智慧园区 AI 服务"
    API_V1_PREFIX: str = "/api/v1"

    # 模型路径
    MODELS_DIR: str = "app/models"

    # Ollama
    OLLAMA_BASE_URL: str = "http://localhost:11434"
    OLLAMA_MODEL: str = "qwen2.5:7b-instruct-q4_0"

    # 向量模型
    EMBEDDING_MODEL: str = "bge-small-zh"

    # 向量库（复用业务库 pgvector）—— 必须通过环境变量提供，不硬编码密码
    VECTOR_DB_URL: str

    # 人脸
    FACE_MODEL: str = "buffalo_l"
    FACE_THRESHOLD: float = 0.6

    # 图像识别
    YOLO_MODEL: str = "yolov8n.pt"


settings = Settings()
