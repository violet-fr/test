"""应用配置模块

使用 Pydantic Settings 从 .env 文件读取配置。
安全策略：
- DATABASE_URL、SECRET_KEY 等敏感字段**无默认值**，必须通过环境变量注入
- SECRET_KEY 增加校验器，拒绝弱默认值
- DEBUG 默认 False，防止生产环境泄露调试信息
"""
from typing import List

from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """应用配置类

    字段说明：
    - 无默认值的字段（DATABASE_URL/SECRET_KEY）为必填，启动时若未设置会直接报错
    - 有默认值的字段可通过 .env 覆盖
    """

    model_config = SettingsConfigDict(
        env_file=".env",
        case_sensitive=True,
        extra="ignore",
    )

    # ===== 项目基础 =====
    PROJECT_NAME: str = "智慧园区综合管理平台"
    API_V1_PREFIX: str = "/api/v1"
    # 默认关闭调试。生产环境必须为 False，否则会暴露堆栈和 SQL 语句
    DEBUG: bool = False

    # ===== 数据库 =====
    # 必须通过环境变量提供，格式：postgresql+psycopg://user:password@host:port/dbname
    DATABASE_URL: str

    # ===== Redis =====
    REDIS_URL: str = "redis://localhost:6379/0"

    # ===== JWT =====
    # 必须通过环境变量提供强密钥（建议 32 字符以上随机串）
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 120
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    # ===== 文件上传 =====
    UPLOAD_DIR: str = "static/uploads"
    MAX_UPLOAD_SIZE: int = 10 * 1024 * 1024  # 10MB

    # ===== CORS =====
    # 默认仅允许本地前端域名；生产环境通过环境变量设置实际域名
    CORS_ORIGINS: List[str] = ["http://localhost:5173", "http://127.0.0.1:5173"]

    # ===== AI 服务 =====
    AI_SERVICE_URL: str = "http://localhost:8001"

    @field_validator("SECRET_KEY")
    @classmethod
    def secret_key_not_default(cls, v: str) -> str:
        """校验 SECRET_KEY 不能使用示例默认值

        防止开发者忘记修改导致生产环境用弱密钥。
        """
        if v in {"change-this-secret-key-in-production", "park-secret-key-change-in-production", ""}:
            raise ValueError("SECRET_KEY 必须设置为非默认值的强密钥")
        return v


settings = Settings()
