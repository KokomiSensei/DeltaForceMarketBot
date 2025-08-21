from backend.bot.buyBot2 import BuyBot
from backend.bot.config import BotConfig
from backend.util.monitor import Monitor
from config import Config


class BotService(Monitor):
    def __init__(self, bot: BuyBot) -> None:
        super().__init__()
        self.bot = bot

    @Monitor.synchronized
    def start_bot(self):
        self.bot.controller.start_bot()

    @Monitor.synchronized
    def stop_bot(self):
        self.bot.controller.stop_bot()

    @Monitor.synchronized
    def exit(self):
        self.bot.controller.exit()

    @Monitor.synchronized
    def set_lowest_price(self, lowest_price):
        self.bot.config.lowest_price = lowest_price

    @Monitor.synchronized
    def set_volume(self, volume):
        self.bot.config.volume = volume

    @Monitor.synchronized
    def set_screenshot_delay(self, screenshot_delay):
        self.bot.config.screenshot_delay = screenshot_delay

    @Monitor.synchronized
    def set_debug_mode(self, debug_mode):
        self.bot.config.debug_mode = debug_mode

    @Monitor.synchronized
    def load_config(self, config: BotConfig):
        self.bot.controller.stop_bot()
        self.bot.config = config

    @Monitor.synchronized
    def get_config(self):
        return self.bot.config


bot = BuyBot(Config.skip_bot_model)
bot_service = BotService(bot)
