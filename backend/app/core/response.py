"""统一响应格式：{code, msg, data}"""
from typing import Any, Generic, Optional, TypeVar

from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
from pydantic import BaseModel

T = TypeVar("T")


class ApiResponse(BaseModel, Generic[T]):
    """统一响应模型"""
    code: int = 0
    msg: str = "success"
    data: Optional[T] = None


def success(data: Any = None, msg: str = "success") -> dict:
    """成功响应"""
    return {"code": 0, "msg": msg, "data": data}


def error(code: int, msg: str, data: Any = None) -> dict:
    """失败响应"""
    return {"code": code, "msg": msg, "data": data}


class PageResult(BaseModel, Generic[T]):
    """分页结果"""
    items: list[T]
    total: int
    page: int
    page_size: int


def page_success(items: list, total: int, page: int, page_size: int) -> dict:
    """分页成功响应"""
    return success({
        "items": items,
        "total": total,
        "page": page,
        "page_size": page_size,
    })
