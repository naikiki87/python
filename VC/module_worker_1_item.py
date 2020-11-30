import sys
import time
# import datetime
from datetime import datetime
import pandas as pd
import numpy
import sqlite3
import math
from time import localtime, strftime
from PyQt5.QtWidgets import *
from PyQt5.QAxContainer import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5 import QtTest, QtCore
from collections import deque
import config
import pyupbit
from time import sleep
import func_module
from time import localtime, strftime

file = open('../../individual/upas.txt', 'r')
s = file.read()
key = s.split('\n')

TICKERS = config.TICKER_1_ITEM
# TARGET_PER = config.TARGET_PER
# TARGET_MINUS_PER = -config.TARGET_MINUS_PER
MOVEMENT_MAX = config.MOVEMENT_MAX
BUY_LIM_CNT = config.BUY_LIM_CNT
BUY_LIM_LOW_CNT = config.BUY_LIM_LOW_CNT
NEW_BUY_AMT = config.NEW_BUY_AMT
ADD_WATER_AMT = config.ADD_WATER_AMT
UP_DOWN_HI = config.UP_DOWN_HI
UP_DOWN_LO = config.UP_DOWN_LO

# NEW_BUY_AMT = 5000

TARGET_PER = 1
TARGET_MINUS_PER = -1.5
print("NEW BUY : ", NEW_BUY_AMT)
print("ADD WATER : ", TARGET_MINUS_PER, '%')
print("TARGET PERCENT : ", TARGET_PER, '%')

class Worker(QThread):
    connected = 0
    trans_dict = pyqtSignal(dict)
    th_con = pyqtSignal(int)
    rq_order = pyqtSignal(dict)
    first_jumun_check = pyqtSignal(dict)

    def __init__(self, seq):
        global key
        super().__init__()
        self.seq = seq
        self.item = TICKERS[self.seq]

        access_key = key[0]
        secret_key = key[1]
        self.upbit = pyupbit.Upbit(access_key, secret_key)

        self.movement = []
        self.up_down = []
        self.prev_price = None

        self.order_sell = func_module.sell
        self.order_buy = func_module.buy
        self.order_addwater = func_module.add_water_1_item

        self.prev_percent = None
        self.prev_volume_ratio = None

        self.lock = 0
        self.lock_cnt = 0

        self.uping = 0

    def buy_by_manual(self) :
        print("add water by manual")
        self.order_buy(self.item)

    def sell_by_manual(self) :
        print("sell by manual")
        self.order_sell(self.item)

    def run(self):
        global upbit
        self.th_con.emit(1)
        while True:
            rp_dict = {}
            rp_dict['seq'] = self.seq
            rp_dict['item'] = self.item
            price = pyupbit.get_current_price(self.item)
            rp_dict['price'] = price
            if self.prev_price == None :
                self.prev_price = price
            else :
                if price == None :
                    gap = 0
                else :
                    gap = price - self.prev_price
                if len(self.movement) == MOVEMENT_MAX :
                    self.movement.pop(0)
                if len(self.up_down) == MOVEMENT_MAX :
                    self.up_down.pop(0)

                if gap == 0 :
                    self.movement.append(0)
                    self.up_down.append(0)
                else :
                    self.movement.append(1)
                    if gap < 0 :
                        self.up_down.append(-1)
                    elif gap > 0 :
                        self.up_down.append(1)

                self.prev_price = price

            rp_dict['wave'] = str(sum(self.movement)) + ' / ' + str(sum(self.up_down))

            try :
                up_down = sum(self.up_down)
                if sum(self.movement) >= BUY_LIM_CNT :
                    if up_down <= UP_DOWN_HI and up_down >= UP_DOWN_LO :
                        self.is_there = 0
                        acc_bal = self.upbit.get_balances()      ## 잔고조회
                        for i in range(0, len(acc_bal[0]), 1) :
                            item = acc_bal[0][i]['currency']
                            if item != "KRW" and item in self.item :
                                self.is_there = 1

                        if self.is_there == 1 :
                            a = 1
                        elif self.is_there == 0:
                            for i in range(len(self.movement)) :
                                self.movement[i] = 0
                            self.order_buy(self.item)

                if self.lock == 1 :
                    if self.lock_cnt == 10 :
                        self.lock_cnt = 0
                        self.lock = 0
                    else :
                        self.lock_cnt = self.lock_cnt + 1
                elif self.lock == 0 :

                    orderbook = pyupbit.get_orderbook(self.item)
                    bids_asks = orderbook[0]['orderbook_units']
                    ask_price = bids_asks[0]['ask_price']
                    bid_price = bids_asks[0]['bid_price']
                    ask_size = bids_asks[0]['ask_size']
                    bid_size = bids_asks[0]['bid_size']

                    volume_ratio = round((ask_size / bid_size), 4)
                    rp_dict['ask_price'] = ask_price
                    rp_dict['bid_price'] = bid_price
                    rp_dict['volume_ratio'] = volume_ratio
                    rp_dict['own_count'] = str("-")
                    rp_dict['unit_price'] = str("-")
                    rp_dict['total_buy'] = str("-")

                    unit_price = 0
                    own_count = 0
                
                    acc_bal = self.upbit.get_balances()      ## 잔고조회
                    for i in range(0, len(acc_bal[0]), 1) :
                        item = acc_bal[0][i]['currency']
                        if item != "KRW" and item in self.item :
                            unit_price = float(acc_bal[0][i]['avg_buy_price'])
                            own_count = float(acc_bal[0][i]['balance'])
                            
                            rp_dict['own_count'] = own_count
                            rp_dict['unit_price'] = unit_price
                            rp_dict['total_buy'] = round((own_count * unit_price), 1)

                    if unit_price == 0 :
                        percent = 0
                        self.order_buy(self.item)
                        self.lock = 1
                    else :
                        percent = round((((bid_price - unit_price) / unit_price) * 100), 2)

                    if own_count == 0 :
                        buy_qty_ratio = '-'
                    else :
                        buy_qty_ratio = round((bid_size / own_count), 2)

                    rp_dict['buy_qty_ratio'] = buy_qty_ratio
                    rp_dict['percent'] = percent
                    rp_dict['ordered'] = 0
                    self.trans_dict.emit(rp_dict)


                    if percent >= TARGET_PER :
                        print("<< UP >>")
                        f_sell = open("trade_log.txt",'a')
                        data = self.get_now() + "[UP] item : " + str(self.item) + "percent : " + str(percent) + '\n'
                        f_sell.write(data)
                        f_sell.close()
                        if self.uping == 0 :
                            self.uping = 1
                        
                        if self.uping == 1 :
                            # print(self.item, "[매수물량 비] : ", round((bid_size / own_count), 3))
                            print(self.item, "[매수물량 비] : ", buy_qty_ratio)
                            if buy_qty_ratio < 200 :
                                print("[WO] SELL [매수물량 적음] : ", buy_qty_ratio, "per : ", percent)
                                self.order_sell(self.item)
                                self.lock = 1

                                f_sell = open("trade_log.txt",'a')
                                data = self.get_now() + "[sell buy_qty_low] item : " + str(self.item) + "/ price : " + str(bid_price) + "/ Qty : " + str(own_count) + "percent : " + str(percent) + '\n'
                                f_sell.write(data)
                                f_sell.close()
                            
                            else :
                                if volume_ratio >= 50 :
                                    print("[WO] SELL - Volume Ratio HIGH : ", volume_ratio, "per : ", percent)
                                    self.order_sell(self.item)
                                    self.lock = 1
                                else :
                                    wait = 1

                    

                    elif percent <= TARGET_MINUS_PER :
                        # print("[WO] ADD_WATER : ", percent, TARGET_MINUS_PER)
                        self.order_addwater(self.item)
                        self.lock = 1
                        # f1 = open("trade_log.txt",'a')
                        # data = self.get_now() + "[add water] " + str(self.item) + '\n'
                        # f1.write(data)
                        # f1.close()
                    
                    else :
                        if self.uping == 1 :
                            self.uping = 0

            except :
                pass

            # time.sleep(1)
            sleep(0.5)
    
    def now(self) :

        return datetime.datetime.now()

    def get_now(self) :
        year = strftime("%Y", localtime())
        month = strftime("%m", localtime())
        day = strftime("%d", localtime())
        hour = strftime("%H", localtime())
        cmin = strftime("%M", localtime())
        sec = strftime("%S", localtime())

        now = "[" + year + "/" + month +"/" + day + " " + hour + ":" + cmin + ":" + sec + "] "

        return now