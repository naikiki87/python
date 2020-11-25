import sys
import time
import math
import datetime
import sqlite3
import config
from PyQt5.QtCore import *
from PyQt5 import QtTest, QtCore, QtWidgets
import pandas as pd 
import requests
import threading
from bs4 import BeautifulSoup
from PyQt5.QtWidgets import *
from PyQt5.QAxContainer import *
import pyupbit

file = open('../../individual/upas.txt', 'r')
s = file.read()
key = s.split('\n')

class Timer(QThread):
    cur_time = pyqtSignal(dict)
    timer_connected = pyqtSignal(int)
    cur_balance = pyqtSignal(dict)

    def __init__(self):
        super().__init__()
        global key
        self.timer_on = 1
        access_key = key[0]
        secret_key = key[1]
        self.upbit = pyupbit.Upbit(access_key, secret_key)

    def run(self):
        temp_time = {}
        self.timer_connected.emit(1)
        while True:
            if self.timer_on == 1 :
                now = datetime.datetime.now()
                mkt_open = now.replace(hour=0, minute=0, second=0)
                mkt_close = now.replace(hour=23, minute=59, second=59)

                c_hour = now.strftime('%H')
                c_min = now.strftime('%M')
                c_sec = now.strftime('%S')
                str_time = c_hour + ':' + c_min + ':' + c_sec
                temp_time['time'] = str_time

                self.cur_time.emit(temp_time)       ## 현재시각 및 market status send

                # if (int(c_sec) % 2) == 1 :
                #     try :
                #         acc_bal = self.upbit.get_balances()
                #         temp_bal = {}
                #         total_coin_KRW = 0
                #         for i in range(0, len(acc_bal[0]), 1) :
                #             item = acc_bal[0][i]['currency']
                #             if item == "KRW" :
                #                 cashKRW = float(acc_bal[0][i]['balance'])
                #             else :
                #             # if item =! "KRW" :
                #                 # item = acc_bal[0][i]['currency']
                #                 count = acc_bal[0][i]['balance']
                #                 unit_price = acc_bal[0][i]['avg_buy_price']

                #             total_coin_KRW = total_coin_KRW + (float(unit_price) * float(count))

                #         # cashKRW = float(acc_bal[0][0]['balance'])
                #         temp_bal['cashKRW'] = cashKRW
                #         temp_bal['coinKRW'] = total_coin_KRW
                #         temp_bal['totalKRW'] = cashKRW + total_coin_KRW

                #         self.cur_balance.emit(temp_bal)
                        
                #     except :
                #         pass

                
            time.sleep(1)