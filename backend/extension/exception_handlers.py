import importlib
import inspect
import pkgutil
import traceback
from functools import wraps
from typing import Any, Callable, Type

from flask import Flask, Response, jsonify

import backend.exception as exception_pkg
import backend.exception.base_exception as base_exception_pkg
from backend.exception.base_exception import BaseException
from backend.exception.general_exception import InternalServerError
from backend.util.logger import logger


def register_exception_handlers(app: Flask) -> None:
    def make_handler(exc_cls: Type[BaseException]):
        def handler(e: BaseException) -> tuple[Response, int]:
            logger.error(f"发生异常: {e.message}")
            logger.error("\n".join(traceback.format_exception(type(e), e, e.__traceback__)))
            return jsonify(e.to_dict()), e.STATUS_CODE

        return handler

    # 自动导入 backend.exception 包下所有异常模块
    package_dir: str = list(exception_pkg.__path__)[0]
    package_name: str = exception_pkg.__name__
    for _, module_name, is_pkg in pkgutil.iter_modules([package_dir]):
        if not is_pkg and module_name not in (base_exception_pkg.__name__, "__init__"):
            module = importlib.import_module(f"{package_name}.{module_name}")
            for name, obj in inspect.getmembers(module):  # type: ignore
                if inspect.isclass(obj) and issubclass(obj, BaseException) and obj is not BaseException:
                    app.register_error_handler(obj, make_handler(obj))

    # 添加通用异常处理器，捕获所有其他异常
    @app.errorhandler(Exception)
    def handle_general_exception(e: Exception) -> tuple[Response, int]:  # type: ignore
        # 如果已经是 BaseException 类型，不需要转换
        if isinstance(e, BaseException):
            return make_handler(type(e))(e)

        # 转换为 InternalServerError
        error_msg = f"未处理的异常: {e!s}"
        logger.error(error_msg)
        logger.error("\n".join(traceback.format_exception(type(e), e, e.__traceback__)))

        internal_error = InternalServerError(f"服务器内部错误: {e!s}")
        return jsonify(internal_error.to_dict()), internal_error.STATUS_CODE


def HandlesExceptions(app_factory: Callable[..., Flask]) -> Callable[..., Flask]:
    @wraps(app_factory)
    def wrapper(*args: Any, **kwargs: Any) -> Flask:
        app = app_factory(*args, **kwargs)
        register_exception_handlers(app)
        return app

    return wrapper
