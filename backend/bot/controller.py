
from backend.bot.buyBot2 import BuyBot

class BotController:
    def __init__(self, bot: BuyBot) -> None:
        self.bot = bot

    def start_bot(self):
        self.bot.controller.start_bot()

    def stop_bot(self):
        self.bot.controller.stop_bot()

    def exit(self):
        self.bot.controller.exit()

    def set_lowest_price(self, lowest_price):
        self.bot.lowest_price = lowest_price

    def set_volume(self, volume):
        self.bot.volume = volume

    def set_screenshot_delay(self, screenshot_delay):
        self.bot.screenshot_delay = screenshot_delay
        
    def set_debug_mode(self, debug_mode):
        self.bot.debug_mode = debug_mode
