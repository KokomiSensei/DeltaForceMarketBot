from __future__ import annotations

import threading
import time

import keyboard
import numpy as np
import pyautogui

from backend.bot.config import BotConfig
from backend.bot.constants import PositionalConstants
from backend.util.adminAuth import is_admin, run_as_admin
from backend.util.logger import logger
from backend.util.position_adapter import get_windowshot, mouse_click, mouse_move


class OcrException(Exception):
    pass


class BuyBot:
    class BotController:
        def __init__(self, bot: BuyBot):
            self.bot = bot
            self.running = False
            self.should_exit = False
            self.bot_thread = None

        def start_bot(self):
            """Start the bot in a separate thread if it's not already running"""
            if self.running:
                logger.warning("Bot is already running!")
                return

            self.running = True
            logger.info("Bot started! Press F9 to stop.")
            self.bot_thread = threading.Thread(target=self._bot_loop)
            self.bot_thread.daemon = True
            self.bot_thread.start()

        def stop_bot(self):
            """Signal the bot to stop"""
            if not self.running:
                logger.warning("Bot is not running!")
                return

            logger.info("Stopping bot...")
            self.running = False
            if self.bot_thread and self.bot_thread.is_alive():
                self.bot_thread.join(timeout=2.0)
            logger.info("Bot stopped.")

        def exit(self):
            """Signal the controller to exit the main loop"""
            self.should_exit = True
            self.stop_bot()
            logger.info("Exit requested.")

        def _bot_loop(self):
            """The main bot execution loop that runs in a separate thread"""
            try:
                while self.running:
                    self.bot.massive_purchase()
                    logger.info("massive_purchase returned")
                    time.sleep(0.05)  # Small delay to prevent CPU overuse
            except Exception as e:
                logger.error("Error in bot thread: %s", str(e), exc_info=True)
                self.running = False

    def __init__(self, skip_bot_model):
        logger.info("Initializing BuyBot")
        if skip_bot_model:
            self.reader = None
        else:
            import easyocr

            self.reader = easyocr.Reader(["en"], gpu=True)
        # Use the active configuration
        self.config = BotConfig()
        self.controller = BuyBot.BotController(self)
        logger.debug(
            "BuyBot initialized with config '%s', lowest_price=%s, volume=%s, screenshot_delay=%s",
            self.config.name,
            self.config.lowest_price,
            self.config.volume,
            self.config.screenshot_delay,
        )

    def identify_number(self, img):
        try:
            logger.debug("Running OCR on image")
            text = self.reader.readtext(np.array(img))  # type: ignore
            text = text[-1][1]  # type: ignore
            text = text.replace(",", "")
            text = text.replace(".", "")
            text = text.replace(" ", "")
            result = int(text)
            logger.debug("OCR result: %s", result)
            return result
        except Exception as e:
            logger.error("OCR operation failed: %s", str(e))
            raise OcrException(f"OCR operation failed: {e}") from e

    def identify_price(self):
        if self.config.screenshot_delay > 0:
            time.sleep(self.config.screenshot_delay / 1000.0)
        logger.debug("Taking screenshot for price identification")
        img = get_windowshot(
            PositionalConstants.to_ratio_range(PositionalConstants.PriceRangeTopLeft, PositionalConstants.PriceRangeBottomRight),
        )
        total_price = self.identify_number(img)
        logger.debug("Identified total price: %s", total_price)
        return total_price

    def identify_warning(self):
        if self.config.screenshot_delay > 0:
            time.sleep(self.config.screenshot_delay / 1000.0)
        logger.debug("Taking screenshot for warning identification")
        img = get_windowshot(
            PositionalConstants.to_ratio_range(PositionalConstants.WarningRangeTopLeft, PositionalConstants.WarningRangeBottomRight),
        )
        warning_price = self.identify_number(img)
        logger.debug("Identified warning price: %s", warning_price)
        return warning_price

    def massive_purchase(self):
        avg_price = float("inf")
        schema_button_position = PositionalConstants.Schema.Button(self.config.target_schema_index)
        while True:
            if not self.controller.running:
                logger.debug("Controller not running, exiting massive_purchase")
                return
            try:
                # 两个相同方案来回切，以增加识别频率
                mouse_click(PositionalConstants.to_ratio(PositionalConstants.Schema.Button(1)))
                total_price = self.identify_price()
                avg_price = (total_price / self.config.volume) if self.config.volume > 0 else total_price
                logger.info(
                    f"Total price: {total_price} / Volume: {self.config.volume} = Avg price: {avg_price:.2f}, Lowest: {self.config.lowest_price}",
                )
                if avg_price <= self.config.lowest_price:
                    break

                mouse_click(PositionalConstants.to_ratio(schema_button_position))
                avg_price = (total_price / self.config.volume) if self.config.volume > 0 else total_price
                logger.info(
                    f"Total price: {total_price} / Volume: {self.config.volume} = Avg price: {avg_price:.2f}, Lowest: {self.config.lowest_price}",
                )
                if avg_price <= self.config.lowest_price:
                    break
            except OcrException as e:
                logger.error(f"Error identifying price: {e}")
                return

        logger.info(f"Found good price! Average: {avg_price:.2f} < {self.config.lowest_price}")
        if self.config.debug_mode:
            logger.debug("Debug mode: Moving mouse to purchase button")
            mouse_move(PositionalConstants.to_ratio(PositionalConstants.PurchaseButton))
        else:
            logger.info("Clicking purchase button")
            mouse_click(PositionalConstants.to_ratio(PositionalConstants.PurchaseButton))

        time.sleep(1)
        try:
            warning_price = self.identify_warning()
            pyautogui.press("esc")
        except OcrException as e:
            logger.error(f"Error identifying warning price: {e}")
            logger.info("Probably made a successful purchase!")


if __name__ == "__main__":
    if not is_admin():
        logger.info("Requesting administrator privileges...")
        run_as_admin()

    logger.info("Starting BuyBot application")
    buy_bot = BuyBot(skip_bot_model=False)
    controller = buy_bot.controller

    # Set up keyboard hotkeys
    keyboard.add_hotkey("f8", controller.start_bot)
    keyboard.add_hotkey("f9", controller.stop_bot)
    keyboard.add_hotkey("f7", controller.exit)

    logger.info("Bot controller ready!")
    logger.info("Press F8 to start the bot")
    logger.info("Press F9 to stop the bot")
    logger.info("Press F7 to exit the program")

    # Main loop that just waits for keyboard events
    try:
        while not controller.should_exit:
            time.sleep(0.1)  # Small delay to prevent CPU overuse
    except KeyboardInterrupt:
        logger.info("KeyboardInterrupt received, exiting")
    finally:
        controller.stop_bot()
        logger.info("Program exited.")
