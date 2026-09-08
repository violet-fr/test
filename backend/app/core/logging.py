"""日志配置模块

同时输出到控制台和文件（logs/app.log），方便本地调试和生产排查。
第三方库（SQLAlchemy、uvicorn）日志降为 WARNING，避免刷屏。
"""
import logging
import sys


def setup_logging():
    """配置全局日志

    - 控制台：实时查看请求日志
    - 文件 logs/app.log：持久化记录，配合日志归集工具使用
    - 格式：时间 [级别] 模块名: 消息
    """
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        handlers=[
            logging.StreamHandler(sys.stdout),
            logging.FileHandler("logs/app.log", encoding="utf-8"),
        ],
    )

    # 降低第三方库日志级别，避免 SQL 语句和访问日志刷屏
    logging.getLogger("sqlalchemy.engine").setLevel(logging.WARNING)
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
