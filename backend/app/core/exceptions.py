"""全局异常处理"""
from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from jwt import PyJWTError

from app.core.response import error


class BizException(Exception):
    """业务异常"""
    def __init__(self, code: int, msg: str):
        self.code = code
        self.msg = msg


def register_exception_handlers(app: FastAPI):
    """注册全局异常处理器"""

    @app.exception_handler(BizException)
    async def biz_exception_handler(request: Request, exc: BizException):
        return JSONResponse(content=error(exc.code, exc.msg))

    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(request: Request, exc: RequestValidationError):
        return JSONResponse(content=error(10001, f"参数校验失败: {exc.errors()}"))

    @app.exception_handler(PyJWTError)
    async def jwt_exception_handler(request: Request, exc: PyJWTError):
        return JSONResponse(content=error(11002, "Token 无效或已过期"))

    @app.exception_handler(Exception)
    async def global_exception_handler(request: Request, exc: Exception):
        return JSONResponse(content=error(10000, f"服务器内部错误: {str(exc)}"))
