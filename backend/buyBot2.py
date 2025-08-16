# -*- coding: utf-8 -*-
from __future__ import annotations
from utils import *
from adminAuth import is_admin, run_as_admin
from logger import logger
import time
import easyocr
import numpy as np
import pyautogui
import keyboard
import threading

class DefaultConfig:
    ScreenshotDelayMs = 100
    MinPrice = 608
    Volume = 60*(5+4+21)

class PositionalConstants:
    DeveloperResolution = (2560, 1440)
    SmallScaleSchemaButton  = (266, 593)
    SchemaButton = (261, 690)
    PurchaseButton = (2257, 1154)
    PriceRangeTopLeft = (2200, 1150)
    PriceRangeBottomRight = (2330, 1175)

    @staticmethod
    def get_mapped(coord, resolution = None):
        if resolution is None:
            resolution = PositionalConstants.DeveloperResolution
        maxX, maxY = resolution
        x, y = coord
        x_ratio = maxX / PositionalConstants.DeveloperResolution[0]
        y_ratio = maxY / PositionalConstants.DeveloperResolution[1]
        return (int(x * x_ratio), int(y * y_ratio))
    
    @staticmethod
    def to_ratio(range):
        x, y = range
        X, Y = PositionalConstants.DeveloperResolution
        return x/X, y/Y
    
    @staticmethod
    def to_ratio_range(coord1, coord2):
        x1, y1 = PositionalConstants.to_ratio(coord1)
        x2, y2 = PositionalConstants.to_ratio(coord2)
        return (x1, y1, x2, y2)

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
        self.debug_mode = True
        self.controller = BuyBot.BotController(self)
        logger.debug("BuyBot initialized with lowest_price=%s, volume=%s, screenshot_delay=%s", 
                    self.lowest_price, self.volume, self.screenshot_delay)

    def identify_number(self, img):
        try:
            logger.debug("Running OCR on image")
            text = self.reader.readtext(np.array(img))
            text = text[-1][1]
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

    def massive_purchase(self):
        avg_price = 9999999
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
            pyautogui.press('esc')
            pyautogui.press('l')
            if self.debug_mode:
                mouse_click(PositionalConstants.to_ratio(PositionalConstants.SmallScaleSchemaButton))
            else:
                mouse_click(PositionalConstants.to_ratio(PositionalConstants.SchemaButton))

        logger.info(f"Found good price! Average: {avg_price:.2f} < {self.lowest_price}")
        if self.debug_mode:
            logger.debug("Debug mode: Moving mouse to purchase button")
            # mouse_move(PositionalConstants.to_ratio(PositionalConstants.PurchaseButton))
            mouse_click(PositionalConstants.to_ratio(PositionalConstants.PurchaseButton))
        else:
            logger.info("Clicking purchase button")
            mouse_click(PositionalConstants.to_ratio(PositionalConstants.PurchaseButton))


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
