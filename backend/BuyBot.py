# -*- coding: utf-8 -*-

if __name__ == '__main__':
    from backend.utils import *
else:
    from backend.utils import *
import time
import easyocr
import numpy as np
from PyQt5.QtCore import QThread
from config import DefaultConfig


class BuyBot:
    def __init__(self):
        self.reader = easyocr.Reader(['en'], gpu=True)
        self.range_isconvertible_lowest_price = [2179/2560, 1078/1440, 2308/2560, 1102/1440]
        self.range_notconvertible_lowest_price = [2179/2560, 1156/1440, 2308/2560, 1178/1440]
        self.postion_isconvertible_max_shopping_number = [0.9085, 0.7222]
        self.postion_isconvertible_min_shopping_number = [0.8095, 0.7222]  #"将Buybot.py中的"self.postion_isconvertible_min_shopping_number"临时改为[0.8095, 0.7222], 该值原本为[0.7921, 0.7222]"
        self.postion_notconvertiable_max_shopping_number = [2329/2560, 1112/1440]
        self.postion_notconvertiable_min_shopping_number = [2059/2560, 1112/1440] #"将Buybot.py中的"self.postion_notconvertiable_min_shopping_number"临时改为[2059/2560, 1112/1440], 该值原本为[2028/2560, 1112/1440]"
        self.postion_isconvertible_buy_button = [2189/2560, 0.7979]
        self.postion_notconvertiable_buy_button = [2186/2560, 1225/1440]
        self.postion_balance = [2200/2560, 70/1440]
        self.postion_balance_half_coin = [1930/2560, 363/1440, 2324/2560, 387/1440]
        self.lowest_price = None
        self.balance_half_coin = None
        print('初始化完成')
    
    def set_worker(self, worker: QThread):
        self.worker = worker
    
    def identify_number(self, img, debug_mode = False):
        try:
            text = self.reader.readtext(np.array(img))
            text = text[-1][1]
            text = text.replace(',', '')
            text = text.replace('.', '')
            text = text.replace(' ', '')
        except:
            text = None
        if debug_mode == True:
            print(text)
        return int(text) if text else None

    def detect_price(self,  is_convertible: bool, debug_mode = False, wait_ms: int = DefaultConfig.SCREENSHOT_DELAY_MS):
        if wait_ms > 0:
            self.worker.msleep(wait_ms)
        if is_convertible:
            self._screenshot = get_windowshot(self.range_isconvertible_lowest_price, debug_mode=debug_mode)
        else:
            self._screenshot = get_windowshot(self.range_notconvertible_lowest_price, debug_mode=debug_mode)
        # 识别最低价格
        self.lowest_price = self.identify_number(self._screenshot)

        if self.lowest_price == None:
            print('识别失败, 建议检查物品是否可兑换')
            raise Exception('识别失败')
        return int(self.lowest_price)

    def detect_balance_half_coin(self, wait_ms: int = DefaultConfig.SCREENSHOT_DELAY_MS, debug_mode = False):
        # 先把鼠标移到余额位置
        mouse_move(self.postion_balance)
        # 对哈夫币余额范围进行截图然后识别
        if wait_ms > 0:
            self.worker.msleep(wait_ms)
        self._screenshot = get_windowshot(self.postion_balance_half_coin, debug_mode=debug_mode)
        self.balance_half_coin = self.identify_number(self._screenshot)

        if self.balance_half_coin == None:
            print('哈夫币余额检测识别失败或不稳定，建议关闭余额识别相关功能')
        return self.balance_half_coin
    
    def get_half_coin_diff(self, wait_ms: int = DefaultConfig.SCREENSHOT_DELAY_MS):
        previous_balance_half_coin = self.balance_half_coin
        self.detect_balance_half_coin(wait_ms)
        return self.balance_half_coin - previous_balance_half_coin

    def buy(self, is_convertible):
        if is_convertible:
            mouse_click(self.postion_isconvertible_max_shopping_number)
            mouse_click(self.postion_isconvertible_buy_button)
        else:
            mouse_click(self.postion_notconvertiable_max_shopping_number)
            mouse_click(self.postion_notconvertiable_buy_button)
            
    def refresh(self, is_convertible):
        if is_convertible:
            mouse_click(self.postion_isconvertible_min_shopping_number)
            mouse_click(self.postion_isconvertible_buy_button)
        else:
            mouse_click(self.postion_notconvertiable_min_shopping_number)
            mouse_click(self.postion_notconvertiable_buy_button)

    def freerefresh(self, good_postion):
        # esc回到商店页面
        pyautogui.press('esc')
        # 点击回到商品页面
        mouse_click(good_postion)

def main():
    bot = BuyBot()
    print(bot.detect_price(is_convertible=True,debug_mode=True))
    print(bot.detect_balance_half_coin(debug_mode=True)) 

if __name__ == '__main__':
    main()
