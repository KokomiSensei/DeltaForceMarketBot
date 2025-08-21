from backend.app import app
from backend.controller import *  # noqa
from config import Config

# TODO logger?
if __name__ == "__main__":
    app.run(host=Config.host, port=Config.port, debug=Config.run_in_debug_mode, use_reloader=Config.use_reloader)
