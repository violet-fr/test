"""安全模块：密码哈希 + JWT 双令牌机制

设计决策：
1. 密码用 bcrypt（而非 SHA256/MD5）：bcrypt 自带盐值且计算慢，能抵抗暴力破解
2. JWT 双 Token 机制：
   - access_token（2小时）：请求时携带，过期快，降低被盗风险
   - refresh_token（7天）：仅用于换新 access_token，不参与业务请求
   这样即使 access_token 泄露，攻击者也只能用 2 小时；
   而 refresh_token 不随业务请求发送，泄露概率更低。
3. Token 中不存敏感信息（如角色列表），仅存用户ID，角色每次从库查，保证权限变更实时生效。
"""
from datetime import datetime, timedelta, timezone
from typing import Optional

import bcrypt
import jwt

from app.core.config import settings


def hash_password(password: str) -> str:
    """密码哈希

    使用 bcrypt 自动生成盐值并哈希。bcrypt.gensalt() 默认 rounds=12，
    单次哈希约 250ms，足以抵御离线暴力破解。
    返回字符串格式如：$2b$12$...，可直接存入数据库。
    """
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")


def verify_password(password: str, hashed: str) -> bool:
    """验证密码

    bcrypt.checkpw 会自动从哈希值中提取盐值，无需单独存盐。
    内部使用恒定时间比较，防止时序攻击。
    """
    return bcrypt.checkpw(password.encode("utf-8"), hashed.encode("utf-8"))


def create_access_token(subject: str, extra: Optional[dict] = None) -> str:
    """创建访问令牌（access_token）

    Args:
        subject: 用户ID的字符串形式，作为 JWT 的 sub 字段
        extra: 额外载荷（如需要可传角色等，但建议不存，每次从库查）

    Returns:
        JWT 字符串，有效期 ACCESS_TOKEN_EXPIRE_MINUTES（默认2小时）
    """
    expire = datetime.now(timezone.utc) + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    # type 字段用于区分 access 和 refresh，防止用 refresh_token 当 access 用
    payload = {"sub": subject, "exp": expire, "type": "access"}
    if extra:
        payload.update(extra)
    return jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.ALGORITHM)


def create_refresh_token(subject: str) -> str:
    """创建刷新令牌（refresh_token）

    有效期 7 天，仅用于调用 /auth/refresh 换新 access_token。
    不携带任何业务权限信息。
    """
    expire = datetime.now(timezone.utc) + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
    payload = {"sub": subject, "exp": expire, "type": "refresh"}
    return jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.ALGORITHM)


def decode_token(token: str) -> dict:
    """解码并校验 JWT

    自动校验签名和过期时间，失败时抛出 jwt.PyJWTError（由全局异常处理器捕获）。
    """
    return jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
