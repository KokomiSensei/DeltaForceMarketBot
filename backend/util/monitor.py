import threading
from functools import wraps


class Monitor:
    def __init__(self):
        self.lock = threading.RLock()

    @staticmethod
    def synchronized(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            with args[0].lock:
                return func(*args, **kwargs)

        return wrapper
