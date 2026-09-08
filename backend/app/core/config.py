"""应用配置"""
from pydantic_settings import BaseSettings
from typing import List


class Settings(BaseSettings):
    """应用配置，从 .env 读取"""

    # 项目
    PROJECT_NAME: str = "智慧园区综合管理平台"
    API_V1_PREFIX: str = "/api/v1"
    DEBUG: bool = True

    # 数据库
    DATABASE_URL: str = "postgresql+psycopg://park:park123@localhost:5432/smart_park"

    # Redis
    REDIS_URL: str = "redis://localhost:6379/0"

    # JWT
    SECRET_KEY: str = "change-this-secret-key-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 120
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    # 文件上传
    UPLOAD_DIR: str = "static/uploads"
    MAX_UPLOAD_SIZE: int = 10 * 1024 * 1024  # 10MB

    # CORS
    CORS_ORIGINS: List[str] = ["*"]

    # AI 服务
    AI_SERVICE_URL: str = "http://localhost:8001"

    model_config = {"env_file": ".env", "case_sensitive": True}


settings = Settings()
