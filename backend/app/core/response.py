"""统一响应格式模块

全平台接口统一返回格式：
{
    "code": 0,        // 0=成功，非0=失败，错误码分段见 API接口定义.md
    "msg": "success", // 提示信息
    "data": {...}     // 业务数据
}

设计理由：
- 前端只需判断 code===0，统一处理成功/失败，无需每个接口单独写异常分支
- 错误码分段（系统1xxxx/业务2xxxx/AI 3xxxx）便于前端按模块定位问题
- data 统一用对象，即使单值也包一层，方便后续扩展字段而不破坏前端
"""
from typing import Any, Generic, Optional, TypeVar

from pydantic import BaseModel

T = TypeVar("T")


class ApiResponse(BaseModel, Generic[T]):
    """统一响应模型（用于 Swagger 文档展示）

    实际接口返回 dict 而非此模型，此模型仅用于生成 OpenAPI 文档时的类型标注。
    """
    code: int = 0
    msg: str = "success"
    data: Optional[T] = None


def success(data: Any = None, msg: str = "success") -> dict:
    """成功响应

    Args:
        data: 业务数据，可以是 dict/list/str/None
        msg: 提示信息，默认 "success"
    """
    return {"code": 0, "msg": msg, "data": data}


def error(code: int, msg: str, data: Any = None) -> dict:
    """失败响应

    Args:
        code: 错误码（见 API接口定义.md 的错误码分段表）
        msg: 错误提示，直接展示给用户
        data: 附加错误详情（如字段校验错误列表）
    """
    return {"code": code, "msg": msg, "data": data}


class PageResult(BaseModel, Generic[T]):
    """分页结果模型"""
    items: list[T]
    total: int
    page: int
    page_size: int


def page_success(items: list, total: int, page: int, page_size: int) -> dict:
    """分页成功响应

    统一分页结构，前端通用分页组件可直接消费。
    items 为当前页数据列表，total 为符合条件的总记录数。
    """
    return success({
        "items": items,
        "total": total,
        "page": page,
        "page_size": page_size,
    })
