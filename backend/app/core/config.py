"""应用配置"""
from typing import List

from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """应用配置，从 .env 读取。敏感字段无默认值，必须通过环境变量注入。"""

    model_config = SettingsConfigDict(
        env_file=".env",
        case_sensitive=True,
        extra="ignore",
    )

    # 项目
    PROJECT_NAME: str = "智慧园区综合管理平台"
    API_V1_PREFIX: str = "/api/v1"
    # 默认关闭调试，生产环境不会泄露调试信息
    DEBUG: bool = False

    # 数据库 —— 必须通过环境变量提供，不硬编码密码
    DATABASE_URL: str

    # Redis
    REDIS_URL: str = "redis://localhost:6379/0"

    # JWT —— 必须通过环境变量提供
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 120
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    # 文件上传
    UPLOAD_DIR: str = "static/uploads"
    MAX_UPLOAD_SIZE: int = 10 * 1024 * 1024  # 10MB

    # CORS —— 生产环境通过环境变量指定具体域名，默认仅本地
    CORS_ORIGINS: List[str] = ["http://localhost:5173", "http://127.0.0.1:5173"]

    # AI 服务
    AI_SERVICE_URL: str = "http://localhost:8001"

    @field_validator("SECRET_KEY")
    @classmethod
    def secret_key_not_default(cls, v: str) -> str:
        if v in {"change-this-secret-key-in-production", "park-secret-key-change-in-production", ""}:
            raise ValueError("SECRET_KEY 必须设置为非默认值的强密钥")
        return v


settings = Settings()
