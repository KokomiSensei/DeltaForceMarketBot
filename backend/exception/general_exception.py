from typing import override

from backend.exception.base_exception import BaseException


class AuthenticationError(BaseException):
    """认证失败（未登录或凭证无效）"""

    def __init__(self, message: str = "认证失败（未登录或凭证无效）"):
        super().__init__(message)

    @property
    @override
    def STATUS_CODE(self) -> int:
        return 401


class AuthorizationError(BaseException):
    """权限不足"""

    def __init__(self, message: str = "权限不足"):
        super().__init__(message)

    @property
    @override
    def STATUS_CODE(self) -> int:
        return 403


class BadRequestError(BaseException):
    """请求参数错误"""

    def __init__(self, message: str = "请求参数错误"):
        super().__init__(message)

    @property
    @override
    def STATUS_CODE(self) -> int:
        return 400


class NotFoundError(BaseException):
    """资源不存在（404）"""

    def __init__(self, message: str = "资源不存在"):
        super().__init__(message)

    @property
    @override
    def STATUS_CODE(self) -> int:
        return 404


class ConflictError(BaseException):
    """资源冲突（409）。

    比如创建资源时,资源已经存在
    """

    def __init__(self, message: str = "资源冲突"):
        super().__init__(message)

    @property
    @override
    def STATUS_CODE(self) -> int:
        return 409


class DatabaseError(BaseException):
    """数据库操作失败"""

    def __init__(self, message: str = "数据库操作失败"):
        super().__init__(message)

    @property
    @override
    def STATUS_CODE(self) -> int:
        return 500


class InternalServerError(BaseException):
    """服务器内部错误"""

    def __init__(self, message: str = "服务器内部错误"):
        super().__init__(message)

    @property
    @override
    def STATUS_CODE(self) -> int:
        return 500


class BusinessLogicError(BaseException):
    """业务逻辑校验失败"""

    def __init__(self, message: str = "业务逻辑校验失败"):
        super().__init__(message)

    @property
    @override
    def STATUS_CODE(self) -> int:
        return 422


class ExternalServiceError(BaseException):
    """外部服务调用失败"""

    def __init__(self, message: str = "外部服务调用失败"):
        super().__init__(message)

    @property
    @override
    def STATUS_CODE(self) -> int:
        return 502
