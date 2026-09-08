"""全局异常处理模块

设计思路：
- 所有异常统一转换为 {code, msg, data} 格式返回，前端只需处理一种响应结构
- 异常按"从具体到通用"的顺序注册，FastAPI 会按注册顺序匹配
- 生产环境应去掉全局异常中的 str(exc)，避免泄露堆栈信息
"""
from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from jwt import PyJWTError

from app.core.response import error


class BizException(Exception):
    """业务异常

    业务代码中用 `raise BizException(12001, "用户不存在")` 抛出，
    全局处理器会自动转为统一响应格式。
    这样避免了在每个接口里手写 `return error(...)`，代码更简洁。
    """
    def __init__(self, code: int, msg: str):
        self.code = code
        self.msg = msg


def register_exception_handlers(app: FastAPI):
    """注册全局异常处理器

    在 main.py 中调用一次即可。处理优先级：
    BizException > RequestValidationError > PyJWTError > Exception
    """

    @app.exception_handler(BizException)
    async def biz_exception_handler(request: Request, exc: BizException):
        """业务异常：直接返回预定义的错误码和提示"""
        return JSONResponse(content=error(exc.code, exc.msg))

    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(request: Request, exc: RequestValidationError):
        """请求参数校验失败：返回具体错误字段，便于前端定位"""
        return JSONResponse(content=error(10001, f"参数校验失败: {exc.errors()}"))

    @app.exception_handler(PyJWTError)
    async def jwt_exception_handler(request: Request, exc: PyJWTError):
        """JWT 相关异常（签名错误/过期/格式不对）"""
        return JSONResponse(content=error(11002, "Token 无效或已过期"))

    @app.exception_handler(Exception)
    async def global_exception_handler(request: Request, exc: Exception):
        """兜底异常：捕获所有未处理异常

        注意：生产环境应改为返回模糊提示（如"服务器开小差了"），
        这里 str(exc) 仅用于开发调试。
        """
        return JSONResponse(content=error(10000, f"服务器内部错误: {str(exc)}"))
