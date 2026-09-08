"""数据库连接模块

技术选型说明：
- 使用 SQLAlchemy 2.0 同步模式（而非 async），原因：
  1. 与 pgvector 扩展兼容性更好，向量检索 API 更稳定
  2. 业务后端以 CRUD 为主，同步模型已足够，避免 async 带来的连接池复杂度
  3. 团队学习成本低，便于多小组并行开发
- 使用连接池 + pool_pre_ping，避免长连接被数据库端断开后报错
"""
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase

from app.core.config import settings

# SQLAlchemy 引擎：整个应用共享一个实例
# - pool_pre_ping=True: 每次取连接前先 ping，自动剔除失效连接（防止 8 小时空闲断开）
# - pool_size=10 / max_overflow=20: 连接池大小，单机部署足够支撑并发
# - echo=settings.DEBUG: 开发环境打印 SQL，生产环境关闭
engine = create_engine(
    settings.DATABASE_URL,
    pool_pre_ping=True,
    pool_size=10,
    max_overflow=20,
    echo=settings.DEBUG,
)

# 会话工厂：autocommit=False 强制显式提交，避免误写数据
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


class Base(DeclarativeBase):
    """所有 ORM 模型的基类

    使用 DeclarativeBase（SQLAlchemy 2.0 推荐写法）替代旧式 declarative_base()。
    所有业务模型继承 BaseModel（见 app.models.base），BaseModel 再继承本类，
    从而获得 id / created_at / updated_at 通用字段。
    """
    pass


def get_db():
    """FastAPI 依赖注入：获取数据库会话

    用法：在路由函数参数中声明 `db: Session = Depends(get_db)`，
    FastAPI 会自动注入会话并在请求结束后关闭（finally 块）。
    这样做的好处是：
    - 每个请求使用独立会话，线程安全
    - 请求结束自动关闭，不会泄漏连接
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
