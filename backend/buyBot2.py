# -*- coding: utf-8 -*-
import sys
import os
import ctypes

def is_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False

def run_as_admin():
    script = os.path.abspath(sys.argv[0])
    params = ' '.join(sys.argv[1:])
    
    ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, f'"{script}" {params}', None, 1)
    sys.exit(0)

if __name__ == '__main__':
    from utils import *
else:
    from backend.utils import *
import time
import easyocr
import numpy as np
import pyautogui
import keyboard
import threading

class DefaultConfig:
    ScreenshotDelayMs = 100
    MinPrice = 608
    Volumn = 60*(5+4+21)

class PositionalConstants:
    DeveloperResolution = (2560, 1440)
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
        def __init__(self, bot):
            self.bot = bot
            self.running = False
            self.should_exit = False
            self.bot_thread = None
        
        def start_bot(self, debug_mode=True):
            """Start the bot in a separate thread if it's not already running"""
            if self.running:
                print("Bot is already running!")
                return
            
            self.running = True
            print("Bot started! Press F9 to stop.")
            self.bot_thread = threading.Thread(target=self._bot_loop, args=(debug_mode,))
            self.bot_thread.daemon = True
            self.bot_thread.start()
        
        def stop_bot(self):
            """Signal the bot to stop"""
            if not self.running:
                print("Bot is not running!")
                return
            
            print("Stopping bot...")
            self.running = False
            if self.bot_thread and self.bot_thread.is_alive():
                self.bot_thread.join(timeout=2.0)
            print("Bot stopped.")
        
        def exit(self):
            """Signal the controller to exit the main loop"""
            self.should_exit = True
            self.stop_bot()
        
        def _bot_loop(self, debug_mode):
            """The main bot execution loop that runs in a separate thread"""
            try:
                while self.running:
                    self.bot.massive_purchase(debug_mode=debug_mode)
                    time.sleep(0.1)  # Small delay to prevent CPU overuse
            except Exception as e:
                print(f"Error in bot thread: {e}")
                self.running = False
                
    def __init__(self):
        self.reader = easyocr.Reader(['en'], gpu=True)
        self.lowest_price = DefaultConfig.MinPrice
        self.volumn = DefaultConfig.Volumn
        self.screenshot_delay = DefaultConfig.ScreenshotDelayMs
        self.controller = BuyBot.BotController(self)

    def identify_number(self, img, debug_mode = False):
        try:
            text = self.reader.readtext(np.array(img))
            text = text[-1][1]
            text = text.replace(',', '')
            text = text.replace('.', '')
            text = text.replace(' ', '')
        except Exception as e:
            raise OcrException(f"OCR operation failed: {e}") from e
        return int(text)

    def identify_price(self, debug_mode = False):
        if self.screenshot_delay > 0:
            time.sleep(self.screenshot_delay / 1000.0)
        img = get_windowshot(PositionalConstants.to_ratio_range(PositionalConstants.PriceRangeTopLeft, PositionalConstants.PriceRangeBottomRight), debug_mode=debug_mode)
        total_price = self.identify_number(img, debug_mode=debug_mode)
        return total_price

    def massive_purchase(self, debug_mode = False):
        avg_price = 9999999
        while True:
            if not self.controller.running:
                return
            try:
                total_price = self.identify_price(debug_mode=debug_mode)
                avg_price = (total_price / self.volumn) if self.volumn > 0 else total_price
                print(f"Total price: {total_price} / Volume: {self.volumn} = Avg price: {avg_price}, Lowest: {self.lowest_price}")
                if avg_price <= self.lowest_price:
                    break
            except OcrException as e:
                print(f"Error identifying price: {e}")
            pyautogui.press('esc')
            pyautogui.press('l')
            mouse_click(PositionalConstants.to_ratio(PositionalConstants.SchemaButton))

        print(f"Average price: {avg_price} < {self.lowest_price}")
        print("Purchase button clicked")
        if debug_mode:
            mouse_move(PositionalConstants.to_ratio(PositionalConstants.PurchaseButton))
        else:
            mouse_click(PositionalConstants.to_ratio(PositionalConstants.PurchaseButton))


if __name__ == '__main__':
    if not is_admin():
        print("Requesting administrator privileges...")
        run_as_admin()
    
    buy_bot = BuyBot()
    controller = buy_bot.controller

    # Set up keyboard hotkeys
    keyboard.add_hotkey('f8', controller.start_bot, args=(False,))
    keyboard.add_hotkey('f9', controller.stop_bot)
    keyboard.add_hotkey('f7', controller.exit)
    
    print("Bot controller ready!")
    print("Press F8 to start the bot")
    print("Press F9 to stop the bot")
    print("Press F7 to exit the program")
    
    # Main loop that just waits for keyboard events
    try:
        while not controller.should_exit:
            time.sleep(0.1)  # Small delay to prevent CPU overuse
    except KeyboardInterrupt:
        pass
    finally:
        controller.stop_bot()
        print("Program exited.")
