"""Redis 客户端模块

设计说明：
- 使用 redis-py 同步客户端（与 SQLAlchemy 同步模式保持一致，避免混用 async）
- decode_responses=True：自动将字节解码为字符串，业务层无需手动 decode
- 优雅降级：Redis 不可用时不抛出致命错误，核心业务（登录/鉴权）仍可正常运行；
  缓存类功能（验证码、限流、热点数据）自动跳过，保证高可用

生产环境用途：
1. 验证码/短信码存储（带过期时间）
2. 接口限流计数
3. JWT 黑名单（用户登出/改密后 Token 失效）
4. 热点数据缓存（菜单树、字典等低频变更数据）
"""
import logging

import redis
from redis.exceptions import RedisError

from app.core.config import settings

logger = logging.getLogger(__name__)

# 全局 Redis 客户端实例（整个应用共享）
# socket_connect_timeout/socket_timeout：避免 Redis 故障时请求长时间阻塞
# 连接池由 redis-py 内部管理，无需手动创建
redis_client: redis.Redis | None = None


def init_redis() -> None:
    """初始化 Redis 连接

    在应用启动时（lifespan）调用。
    连接失败时仅记录警告，不中断应用启动——核心功能不依赖 Redis。
    """
    global redis_client
    try:
        redis_client = redis.Redis.from_url(
            settings.REDIS_URL,
            decode_responses=True,
            socket_connect_timeout=3,
            socket_timeout=3,
            socket_keepalive=True,
            health_check_interval=30,
        )
        # 主动 ping 一次，验证连接可用（失败会抛 RedisError）
        redis_client.ping()
        logger.info("Redis 连接成功")
    except RedisError as e:
        logger.warning("Redis 连接失败，缓存功能将不可用（不影响核心业务）: %s", e)
        redis_client = None


def get_redis() -> redis.Redis | None:
    """获取 Redis 客户端

    返回 None 表示 Redis 不可用，调用方应做降级处理：
        r = get_redis()
        if r:
            r.setex("key", 300, "value")
        # else: 跳过缓存逻辑
    """
    return redis_client


def close_redis() -> None:
    """关闭 Redis 连接池，应用关闭时调用"""
    global redis_client
    if redis_client is not None:
        try:
            redis_client.close()
        except RedisError:
            pass
        redis_client = None
