"""通用 Schema"""
from typing import Optional

from pydantic import BaseModel


class PageParams(BaseModel):
    """分页参数"""
    page: int = 1
    page_size: int = 20
