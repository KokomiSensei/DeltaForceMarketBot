import keyboard

from backend import controller
from backend.app import app
from backend.controller import *  # noqa
from backend.util.adminAuth import is_admin, run_as_admin
from backend.util.logger import logger
from config import Config


def init():
    if not is_admin():
        logger.info("Requesting administrator privileges...")
        run_as_admin()
    logger.info("Running with administrator privileges...")

    # Set up keyboard hotkeys
    keyboard.add_hotkey("f8", controller.start_bot)
    keyboard.add_hotkey("f9", controller.stop_bot)

    logger.info("Bot controller ready!")
    logger.info("Press F8 to start the bot")
    logger.info("Press F9 to stop the bot")


# TODO logger?
if __name__ == "__main__":
    init()
    app.run(host=Config.host, port=Config.port, debug=Config.run_in_debug_mode, use_reloader=Config.use_reloader)
