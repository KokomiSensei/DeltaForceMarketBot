# from dataclasses import is_dataclass
import inspect
from enum import Enum
from functools import wraps
from typing import Any, Callable, Dict, List, Optional, Type, get_args, override

import jsons  # type: ignore
from flask import Blueprint, Response, jsonify, request
from flask.views import MethodView
from pydantic import BaseModel, TypeAdapter

from backend.app import app
from backend.exception.general_exception import (
    BadRequestError,
    InternalServerError,
)
from backend.util.logger import logger


# 注册pydantic BaseModel的解析方法
def _pydantic_base_model_serializer(obj: BaseModel, **kwargs):  # type: ignore
    return obj.model_dump()


jsons.set_serializer(_pydantic_base_model_serializer, BaseModel)  # type: ignore


class JsonConversionError(InternalServerError):
    @override
    def __init__(self, message: str = "JSON转换失败") -> None:
        super().__init__(message)
        self.message = message


adapters: Dict[Any, TypeAdapter[Any]] = {}


def WithName(name: Optional[str] = None):
    def decdec(
        dec: Callable[..., Any],
    ) -> Callable[..., Any]:  # decorator that decorates a decorator
        @wraps(dec)
        def newdec(func: Callable[..., Any]) -> Callable[..., Any]:
            deced = dec(func)  # func decorated by dec

            if not hasattr(func, "decorators"):
                func.__dict__["decorators"] = set()  # type: ignore
            decorators: set[str] = func.__dict__["decorators"]  # type: ignore
            decorator_name = name if name else dec.__name__
            decorators.add(decorator_name)
            deced.__dict__["decorators"] = decorators
            logger.debug(f"装饰器 {decorator_name} 被添加到函数 {func.__name__} 的装饰器列表中")
            logger.debug(f"函数 {func.__name__} 的装饰器列表为 {decorators}")
            return deced

        return newdec

    return decdec


def get_type_adapter(cls: Any) -> TypeAdapter[Any]:
    if cls in adapters:
        return adapters[cls]
    adapter = TypeAdapter(cls)
    adapters[cls] = adapter
    return adapter


# @WithName()
def ResponseBody(func: Callable[..., Any]) -> Callable[..., Response]:
    @wraps(func)
    def wrapper(*args: Any, **kwargs: Any) -> Response:
        result = func(*args, **kwargs)
        if result is None:
            logger.warn(f"带有 @{ResponseBody.__name__} 装饰器的函数 {func.__name__} 返回了 None")
            return jsonify(None)
        if isinstance(result, Response):
            return result
        try:
            sig = inspect.signature(func)
            ReturnType = sig.return_annotation

            if ReturnType is None or ReturnType is inspect.Signature.empty:
                return jsonify(jsons.dump(result, ensure_ascii=False))  # type: ignore

            adapter = get_type_adapter(ReturnType)
            # return jsonify(adapter.dump_python(result))
            # return jsonify(adapter.dump_json(result))
            json_bytes = adapter.dump_json(result)
            return Response(json_bytes.decode("utf-8"), mimetype="application/json")

        except Exception as e:
            raise JsonConversionError(f"序列化为JSON失败: {e!s}") from e

    return wrapper


@WithName()
def RequestBody(json_request_handler: Callable[..., Any]) -> Callable[..., Any]:
    @wraps(json_request_handler)
    def wrapper(*args: Any, **kwargs: Any) -> Any:
        if not request.is_json:
            raise BadRequestError(f"带有 @{RequestBody.__name__} 装饰器的函数 {json_request_handler.__name__} 收到了非JSON格式的请求体")

        # 只支持一个参数（排除 self）
        sig = inspect.signature(json_request_handler)
        params = [p for p in sig.parameters.values() if p.name != "self"]
        assert (
            len(params) >= 1
        ), f"带有 @{RequestBody.__name__} 装饰器的函数 {json_request_handler.__name__} 必须将 json 参数作为 除了self 以外的第一个参数"
        param = params[0]

        # 处理请求体
        try:
            json_data = request.get_json()
        except Exception as e:
            raise BadRequestError(f"JSON格式有误 {e}") from e

        if json_data is None:
            logger.warn("请求体为空")
            kwargs[param.name] = None
            return None

        ParamType = param.annotation
        if ParamType is inspect.Parameter.empty:
            raise JsonConversionError(f"{json_request_handler.__name__} 缺少类型注解,无法自动反序列化")

        try:
            adapter = get_type_adapter(ParamType)
            value = adapter.validate_python(json_data)
            adapters[ParamType] = adapter
            kwargs[param.name] = value
        except Exception as e:
            raise BadRequestError(f"JSON反序列化失败: {e!s}") from e
        return json_request_handler(*args, **kwargs)

    # wrapper.__dict__["_has_request_body"] = True
    # wrapper._has_request_body = True  # type: ignore
    return wrapper


# @WithName()
def RequestParam(get_handler: Callable[..., Any]) -> Callable[..., Any]:
    @wraps(get_handler)
    def wrapper(*args: Any, **kwargs: Any) -> Any:
        sig = inspect.signature(get_handler)
        request_args = set(request.args)
        param_items = [(name, param) for name, param in sig.parameters.items() if name != "self"]
        default_keys = {name for name, param in sig.parameters.items() if param.default != inspect.Parameter.empty}

        # 判断是否需要跳过第一个参数（RequestBody注入）
        def get_skip_param() -> Optional[str]:
            skip_param = None
            if param_items:
                first_param, _ = param_items[0]
                if first_param in kwargs or RequestBody.__name__ in get_handler.__dict__.get("decorators", set()):
                    skip_param = first_param
            return skip_param

        skip_param = get_skip_param()

        sig_keys = {name for name, _ in param_items}
        if skip_param:
            sig_keys -= {skip_param}
        extra = request_args - sig_keys
        missing = sig_keys - request_args - set(kwargs)
        missing_required = missing - default_keys

        if extra:
            logger.warn(f"请求参数 {extra} 不在函数签名中")
        if missing_required:
            raise BadRequestError(f"请求参数 {missing_required} 缺失")

        # 获取参数并注入
        for name, param in param_items:
            if name in kwargs or name == skip_param:
                continue
            value = request.args.get(name)
            if value is None or value == "":
                value = None

            if value is None:
                if param.default == inspect.Parameter.empty:
                    raise BadRequestError(f"请求参数 {name} 缺失")
                value = param.default
            else:
                # value_type = param.annotation if param.annotation is not Optional else get_args(param.annotation)[0]
                value_types = get_args(param.annotation)
                value_type = value_types[0] if len(value_types) > 0 else param.annotation
                try:
                    if value_type is bool:
                        match value.lower():
                            case "false" | "0" | "":
                                value = False
                            case _:
                                value = True
                    else:
                        value = value_type(value)
                except Exception as e:
                    raise BadRequestError(f"参数{name}类型转换失败, 应为{param.annotation}") from e
            kwargs[name] = value
        return get_handler(*args, **kwargs)

    return wrapper


def RestfulController(route: str, url_prefix: str = "/", endpoint_name: Optional[str] = None):
    def decorator(cls: Type[MethodView]):
        blueprint_name = cls.__name__.replace("Controller", "").lower()
        bp = Blueprint(blueprint_name, cls.__module__)
        bp.add_url_rule(
            route,
            view_func=cls.as_view(endpoint_name if endpoint_name else blueprint_name),
        )
        # 这里假设 app 已经全局可用
        app.register_blueprint(bp, url_prefix=url_prefix)
        return cls

    return decorator


class RequestMethod(Enum):
    GET = "GET"
    POST = "POST"
    PUT = "PUT"
    DELETE = "DELETE"
    PATCH = "PATCH"


def RequestMapping(
    route: str,
    methods: Optional[List[RequestMethod]] = None,
    url_prefix: str = "/",
    endpoint_name: Optional[str] = None,
):
    methods = methods if methods else [RequestMethod.GET]

    # @WithName(RequestMapping.__name__)
    def decorator(func: Callable[..., Any]) -> Callable[..., Any]:
        # 在 Flask 应用上下文中注册路由
        full_route = url_prefix.rstrip("/") + route

        @app.route(
            rule=full_route,
            methods=[method.value for method in methods],
            endpoint=endpoint_name if endpoint_name else func.__name__,
        )
        @wraps(func)
        def wrapper(*args: Any, **kwargs: Any):
            return func(*args, **kwargs)

        return wrapper

    return decorator


def GetMapping(route: str, url_prefix: str = "/", endpoint_name: Optional[str] = None):
    return RequestMapping(route, [RequestMethod.GET], url_prefix, endpoint_name)


def PostMapping(route: str, url_prefix: str = "/", endpoint_name: Optional[str] = None):
    return RequestMapping(route, [RequestMethod.POST], url_prefix, endpoint_name)


def PutMapping(route: str, url_prefix: str = "/", endpoint_name: Optional[str] = None):
    return RequestMapping(route, [RequestMethod.PUT], url_prefix, endpoint_name)


def DeleteMapping(route: str, url_prefix: str = "/", endpoint_name: Optional[str] = None):
    return RequestMapping(route, [RequestMethod.DELETE], url_prefix, endpoint_name)


def PatchMapping(route: str, url_prefix: str = "/", endpoint_name: Optional[str] = None):
    return RequestMapping(route, [RequestMethod.PATCH], url_prefix, endpoint_name)
