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

file = open('../../individual/upas.txt', 'r')
s = file.read()
key = s.split('\n')

TICKERS = config.TICKERS_1
TARGET_PER = config.TARGET_PER
TARGET_MINUS_PER = config.TARGET_MINUS_PER
MOVEMENT_MAX = config.MOVEMENT_MAX
BUY_LIM_CNT = config.BUY_LIM_CNT
BUY_LIM_LOW_CNT = config.BUY_LIM_LOW_CNT
NEW_BUY_AMT = config.NEW_BUY_AMT
ADD_WATER_AMT = config.ADD_WATER_AMT
UP_DOWN_HI = config.UP_DOWN_HI
UP_DOWN_LO = config.UP_DOWN_LO

print("NEW BUY :", NEW_BUY_AMT)

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

        self.cnt = 0
        self.lock = 0

        self.movement = []
        self.up_down = []
        self.prev_price = None

    def run(self):
        global upbit
        self.th_con.emit(1)
        while True:
            now = datetime.now()
            t_sec = now.second
            
            if t_sec % 3 == 0 :
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
                        # print(self.item, price, self.prev_price)
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
                # rp_dict['wave'] = sum(self.movement)

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
                                # print("there is already ", self.item)
                            elif self.is_there == 0:
                                for i in range(len(self.movement)) :
                                    self.movement[i] = 0
                                self.buy(self.item)

                    orderbook = pyupbit.get_orderbook(self.item)
                    bids_asks = orderbook[0]['orderbook_units']
                    ask_price = bids_asks[0]['ask_price']
                    bid_price = bids_asks[0]['bid_price']
                    rp_dict['ask_price'] = ask_price
                    rp_dict['bid_price'] = bid_price

                    rp_dict['own_count'] = str("-")
                    rp_dict['unit_price'] = str("-")

                    unit_price = 0
                
                    acc_bal = self.upbit.get_balances()      ## 잔고조회
                    # print(acc_bal[0])
                    for i in range(0, len(acc_bal[0]), 1) :
                        item = acc_bal[0][i]['currency']
                        if item != "KRW" and item in self.item :
                            unit_price = float(acc_bal[0][i]['avg_buy_price'])
                            rp_dict['own_count'] = acc_bal[0][i]['balance']
                            rp_dict['unit_price'] = unit_price

                    if unit_price == 0 :
                        percent = 0
                    else :
                        percent = round((((bid_price - unit_price) / unit_price) * 100), 2)

                    rp_dict['percent'] = percent
                    rp_dict['ordered'] = 0
                    self.trans_dict.emit(rp_dict)

                    if percent > TARGET_PER :
                        self.sell(self.item)

                    # if percent < TARGET_MINUS_PER and self.add_water == 0 :
                    # if percent < TARGET_MINUS_PER and self.get_db_step(self.item) == 0 :
                    #     if self.update_db_step(self.item, 1) == 1 :
                    #         self.add_water(self.item)
                    
                    # if percent < TARGET_MINUS_PER and self.get_db_step(self.item) == 1 :
                    #     if self.update_db_step(self.item, 0) == 1 :
                    #         self.sell(self.item)

                    if percent < TARGET_MINUS_PER :
                        self.add_water(self.item)
                except :
                    pass

            time.sleep(1)
    
    def now(self) :
        return datetime.datetime.now()

    def buy(self, item) :
        try :
            orderbook = pyupbit.get_orderbook(item)
            bids_asks = orderbook[0]['orderbook_units']
            ask_price = bids_asks[0]['ask_price']
            bid_price = bids_asks[0]['bid_price']

            qty = round((NEW_BUY_AMT / ask_price), 8)
            print("buy : ", item, "qty : ", qty, "price : ", ask_price)
            ret = self.upbit.buy_limit_order(item, ask_price, qty)
            # print(ret)
        except :
            pass

    def add_water(self, target_item) :
        try :
            orderbook = pyupbit.get_orderbook(target_item)
            bids_asks = orderbook[0]['orderbook_units']
            ask_price = bids_asks[0]['ask_price']
            bid_price = bids_asks[0]['bid_price']

            acc_bal = self.upbit.get_balances()

            for i in range(0, len(acc_bal[0]), 1) :
                item = acc_bal[0][i]['currency']
                if item != "KRW" and item in target_item :
                    count = acc_bal[0][i]['balance']
                    unit_price = acc_bal[0][i]['avg_buy_price']
                    input_money = float(count) * float(unit_price)

            qty = round(((input_money * 1.5) / ask_price), 8)
            print("buy : ", target_item, "qty : ", qty, "price : ", ask_price)
            ret = self.upbit.buy_limit_order(target_item, ask_price, qty)
            # print(ret)
        except :
            pass

    def sell(self, target_item) :
        self.add_water = 0
        print("sell : ", target_item)
        orderbook = pyupbit.get_orderbook(target_item)
        bids_asks = orderbook[0]['orderbook_units']
        ask_price = bids_asks[0]['ask_price']
        bid_price = bids_asks[0]['bid_price']

        acc_bal = self.upbit.get_balances()
        try :
            for i in range(0, len(acc_bal[0]), 1) :
                item = acc_bal[0][i]['currency']
                if item != "KRW" and item in target_item :
                    count = float(acc_bal[0][i]['balance'])
                    unit_price = float(acc_bal[0][i]['avg_buy_price'])
                    locked = float(acc_bal[0][i]['locked'])
                    print("item : ", item, '/', count, '/', unit_price, locked)

            ret = self.upbit.sell_limit_order(target_item, bid_price, count)
            # print("time : ", ret)
            
        except :
            pass

    def get_db_step(self, item):
        conn = sqlite3.connect("item_status.db")
        cur = conn.cursor()
        sql = "select step from STATUS where item = :ITEM"
        cur.execute(sql, {"ITEM" : item})
        row = cur.fetchone()
        conn.close()
        return int(row[0])

    def update_db_step(item, step) :
        conn = sqlite3.connect("item_status.db")
        cur = conn.cursor()
        sql = "update STATUS set step=:STEP where item=:ITEM"
        cur.execute(sql, {"ITEM" : item, "STEP" : step})
        conn.commit()
        conn.close()

        return cur.rowcount
