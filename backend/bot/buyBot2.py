# -*- coding: utf-8 -*-
from __future__ import annotations
from backend.bot.constants import PositionalConstants
from backend.util.position_adapter import mouse_click, mouse_move, get_windowshot
from backend.bot.adminAuth import is_admin, run_as_admin
from backend.bot.logger import logger
import time
import easyocr
import numpy as np
import pyautogui
import keyboard
import threading

class DefaultConfig:
    ScreenshotDelayMs = 150
    MinPrice = 548
    Volume = 3540
    DebugMode = False


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
                    logger.info('massive_purchase returned')
                    time.sleep(5)  # Small delay to prevent CPU overuse
            except Exception as e:
                logger.error("Error in bot thread: %s", str(e), exc_info=True)
                self.running = False
                
    def __init__(self):
        logger.info("Initializing BuyBot")
        self.reader = easyocr.Reader(['en'], gpu=True)
        self.lowest_price = DefaultConfig.MinPrice
        self.volume = DefaultConfig.Volume
        self.screenshot_delay = DefaultConfig.ScreenshotDelayMs
        self.debug_mode = DefaultConfig.DebugMode
        self.controller = BuyBot.BotController(self)
        logger.debug("BuyBot initialized with lowest_price=%s, volume=%s, screenshot_delay=%s", 
                    self.lowest_price, self.volume, self.screenshot_delay)

    def identify_number(self, img):
        try:
            logger.debug("Running OCR on image")
            text = self.reader.readtext(np.array(img))
            text = text[-1][1] # type: ignore
            text = text.replace(',', '')
            text = text.replace('.', '')
            text = text.replace(' ', '')
            result = int(text)
            logger.debug("OCR result: %s", result)
            return result
        except Exception as e:
            logger.error("OCR operation failed: %s", str(e))
            raise OcrException(f"OCR operation failed: {e}") from e

    def identify_price(self):
        if self.screenshot_delay > 0:
            time.sleep(self.screenshot_delay / 1000.0)
        logger.debug("Taking screenshot for price identification")
        img = get_windowshot(PositionalConstants.to_ratio_range(PositionalConstants.PriceRangeTopLeft, PositionalConstants.PriceRangeBottomRight))
        total_price = self.identify_number(img)
        logger.debug("Identified total price: %s", total_price)
        return total_price
    
    def identify_warning(self):
        if self.screenshot_delay > 0:
            time.sleep(self.screenshot_delay / 1000.0)
        logger.debug("Taking screenshot for warning identification")
        img = get_windowshot(PositionalConstants.to_ratio_range(PositionalConstants.WarningRangeTopLeft, PositionalConstants.WarningRangeBottomRight))
        warning_price = self.identify_number(img)
        logger.debug("Identified warning price: %s", warning_price)
        return warning_price

    def massive_purchase(self):
        avg_price = 9999999
        schema_button_position = PositionalConstants.Schema.Button(3) if self.debug_mode else PositionalConstants.Schema.Button(4)
        while True:
            if not self.controller.running:
                logger.debug("Controller not running, exiting massive_purchase")
                return
            try:
                total_price = self.identify_price()
                avg_price = (total_price / self.volume) if self.volume > 0 else total_price
                logger.info(f"Total price: {total_price} / Volume: {self.volume} = Avg price: {avg_price:.2f}, Lowest: {self.lowest_price}")
                if avg_price <= self.lowest_price:
                    break
            except OcrException as e:
                logger.error(f"Error identifying price: {e}")
                return
            logger.debug("Pressing ESC and L keys")
            # TODO: 好像不需要退出去，直接切换方案就能刷新价格。不确定
            # 退出去
            # pyautogui.press('esc')
            # pyautogui.press('l')
            # 直接点另一个方案
            mouse_click(PositionalConstants.to_ratio(PositionalConstants.Schema.Button(0)))
            mouse_click(PositionalConstants.to_ratio(schema_button_position))

        logger.info(f"Found good price! Average: {avg_price:.2f} < {self.lowest_price}")
        if self.debug_mode:
            logger.debug("Debug mode: Moving mouse to purchase button")
            # mouse_move(PositionalConstants.to_ratio(PositionalConstants.PurchaseButton))
            mouse_click(PositionalConstants.to_ratio(PositionalConstants.PurchaseButton))
        else:
            logger.info("Clicking purchase button")
            mouse_click(PositionalConstants.to_ratio(PositionalConstants.PurchaseButton))
        try:
            time.sleep(1)
            warning_price = self.identify_warning()
            if warning_price > self.lowest_price:
                logger.warning(f"Warning price: {warning_price} > Lowest price: {self.lowest_price}")
                pyautogui.press('esc')
                pyautogui.press('l')
                mouse_click(PositionalConstants.to_ratio(schema_button_position))
            else:
                mouse_click(PositionalConstants.to_ratio(PositionalConstants.WarningRangeTopLeft))
        except OcrException as e:
            logger.error(f"Error identifying warning price: {e}")
            logger.info("Probably made a successful purchase!")


if __name__ == '__main__':
    if not is_admin():
        logger.info("Requesting administrator privileges...")
        run_as_admin()
    
    logger.info("Starting BuyBot application")
    buy_bot = BuyBot()
    controller = buy_bot.controller

    # Set up keyboard hotkeys
    keyboard.add_hotkey('f8', controller.start_bot)
    keyboard.add_hotkey('f9', controller.stop_bot)
    keyboard.add_hotkey('f7', controller.exit)
    
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
        pass
    finally:
        controller.stop_bot()
        logger.info("Program exited.")
