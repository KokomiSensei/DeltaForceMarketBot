from datetime import datetime

from flask import Flask
from flask_cors import CORS

from backend.extension.exception_handlers import HandlesExceptions
from config import Config


@HandlesExceptions
def create_app() -> Flask:
    app = Flask(__name__)
    app.config.from_object(Config)
    CORS(app)

    # 直接设置JSON序列化函数
    original_dumps = app.json.dumps

    def custom_dumps(obj, **kwargs):
        def default(o):
            if isinstance(o, datetime):
                return o.isoformat()
            return original_dumps(o, **kwargs)

        return original_dumps(obj, default=default, **kwargs)

    app.json.dumps = custom_dumps

    return app


app = create_app()


@app.route("/")
def index():
    return "backend running..."
