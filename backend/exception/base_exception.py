# base_exception.py
from abc import ABC, abstractmethod


class BaseException(Exception, ABC):
    @property
    @abstractmethod
    def STATUS_CODE(self) -> int:
        """HTTP status code for the exception."""

    def __init__(self, message: str):
        self.message = message

    def to_dict(self) -> dict[str, str | int]:
        return {
            "error": self.__class__.__name__,
            "message": self.message,
            "code": self.STATUS_CODE,
        }
