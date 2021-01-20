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
import module_finder3
from PyQt5.QtWidgets import *
from PyQt5.QAxContainer import *
import target

UNIT_PRICE_HI_LIM = config.UNIT_PRICE_HI_LIM
UNIT_PRICE_LOW_LIM = config.UNIT_PRICE_LOW_LIM
AUTO_BUY_PRICE_LIM = config.AUTO_BUY_PRICE_LIM
ITEM_FINDER_PERCENT = config.ITEM_FINDER_PERCENT
ITEM_FINDER_PERCENT_LOW = config.ITEM_FINDER_PERCENT_LOW
EXCEPT_ITEM = config.EXCEPT_ITEM
DELAY_SEC = config.DELAY_SEC
SLOT_EMPTY = config.NUM_SLOT - config.SLOT_RUN
TARGET_ITEMS = target.ITEMS

NUM_SLOT = config.NUM_SLOT

print("timer SLOT EMPTY : ", SLOT_EMPTY, '/', NUM_SLOT)
print("timer TARGET ITEMS : ", TARGET_ITEMS)

class Timer(QThread):
    cur_time = pyqtSignal(dict)
    check_slot = pyqtSignal(int)
    refresh_status = pyqtSignal(int)
    req_buy = pyqtSignal(dict)
    release_paused = pyqtSignal(int)
    check_real = pyqtSignal(int)
    sig_main_check_jumun = pyqtSignal(int)
    timer_connected = pyqtSignal(int)

    def __init__(self):
        super().__init__()
        self.timer_on = 0
        self.paused = []
        self.paused_remain_sec = []

        for i in range(NUM_SLOT) :
            self.paused.append(0)
            self.paused_remain_sec.append(0)

        self.item_checking = 0
        self.temp_chk_stop = 0
        self.candidate = ""

        self.kiwoom = QAxWidget()
        self.kiwoom.setControl("KHOPENAPI.KHOpenAPICtrl.1")
        self.kiwoom.dynamicCall("CommConnect()")

        self.kiwoom.OnEventConnect.connect(self.event_connect)
        self.kiwoom.OnReceiveTrData.connect(self.receive_tr_data)

        self.checking_test = 0

    def event_connect(self, err_code):
        if err_code == 0 :
            self.timer_on = 1
            self.timer_connected.emit(1)

    def run(self):
        temp_time = {}
        while True:
            if self.timer_on == 1 :
                now = datetime.datetime.now()
                mkt_open = now.replace(hour=9, minute=0, second=0)
                mkt_close = now.replace(hour=15, minute=30, second=0)
                am901 = now.replace(hour=9, minute=0, second=40)
                am910 = now.replace(hour=9, minute=10, second=0)
                am920 = now.replace(hour=9, minute=20, second=0)
                am921 = now.replace(hour=9, minute=21, second=0)
                am930 = now.replace(hour=9, minute=30, second=0)
                am931 = now.replace(hour=9, minute=31, second=0)
                pm200 = now.replace(hour=14, minute=00, second=0)
                pm230 = now.replace(hour=14, minute=30, second=0)
                pm250 = now.replace(hour=14, minute=50, second=0)
                pm310 = now.replace(hour=15, minute=10, second=0)
                pm320 = now.replace(hour=15, minute=20, second=0)
                check_down_items = now.replace(hour=1, minute=35, second=10)
                double_check = now.replace(hour=15, minute=21, second=0)

                c_hour = now.strftime('%H')
                c_min = now.strftime('%M')
                c_sec = now.strftime('%S')

                str_time = c_hour + ':' + c_min + ':' + c_sec
                temp_time['time'] = str_time

                if now == check_down_items :
                    if self.checking_test == 0 :
                        self.checking_test = 1
                        self.finder3 = module_finder3.Finder()
                        self.finder3.start()

                if now == double_check :
                    if self.checking_test == 0 :
                        self.checking_test = 1
                        self.finder3 = module_finder3.Finder()
                        self.finder3.start()

                if now >= mkt_open and now < mkt_close :
                    temp_time['possible'] = 1
                    temp_time['timezone'] = 0

                    if now >= am920 and c_sec == "00" :
                        self.refresh_status.emit(1)

                    if c_sec == "05" :                      ## 매분마다 실시간 등록여부 갱신
                        self.check_real.emit(1)

                    if now >= am910 and now <= am920 and self.item_checking == 0 :
                        if c_sec == "10" or c_sec == "40" :
                            self.check_slot.emit(1)
                    
                    if now >= am921 and now <= pm230 and self.item_checking == 0 :
                        if c_sec == "10" :
                            self.check_slot.emit(1)
                    
                    if now >= am901 and now<=pm320 and c_sec == "15" :
                        self.sig_main_check_jumun.emit(1)
                    
                    if now >= pm310 :
                        temp_time['timezone'] = 1
                        
                else :
                    temp_time['possible'] = 0
                    temp_time['timezone'] = 0
                self.cur_time.emit(temp_time)       ## 현재시각 및 market status send

                if self.temp_chk_stop > 0 :
                    self.temp_chk_stop = self.temp_chk_stop - 1
                    if self.temp_chk_stop == 0 :
                        self.item_checking = 0

                for i in range(NUM_SLOT) :
                    if self.paused[i] == 1 :
                        if self.paused_remain_sec[i] != 0 :
                            self.paused_remain_sec[i] = self.paused_remain_sec[i] - 1
                        elif self.paused_remain_sec[i] == 0 :
                            self.paused[i] = 0
                            self.release_paused.emit(i)

            time.sleep(1)

    @pyqtSlot(int)
    def rcv_paused(self, data) :
        self.paused[data] = 1
        self.paused_remain_sec[data] = DELAY_SEC

    @pyqtSlot(list)
    def res_check_slot(self, data) :
        self.cur_items = data
        empty = 0

        for i in range(NUM_SLOT) :
            if data[i] == 0 :
                empty = empty + 1

        print(self.now(), "[TIMER] [res_check_slot] empty : ", empty)

        if empty > SLOT_EMPTY and len(TARGET_ITEMS) > 0 :
            self.item_checking = 1
            self.candidate_seq = 0
            self.candidate_queue = []
            self.candidate_queue = TARGET_ITEMS

            # print("res_check_slot : ", self.candidate_queue)
            self.investigate_items()
    
    def investigate_items(self) :
        print("[Investigate Items]")
        # print(self.now(), "[TIMER] [investigate_items] : ", self.candidate_queue, self.candidate_seq)

        if self.candidate_seq >= len(self.candidate_queue) :
            print(self.now(), "[TIMER] [investigate_items] : candidate seq overflow / FINISH")
            self.temp_chk_stop = 180
            # self.item_checking = 0
        else :
            self.candidate = self.candidate_queue[self.candidate_seq]
            if self.candidate in self.cur_items :       ## 기보유중인 항목인 경우
                print("already own item : ", self.candidate)
                self.candidate_seq = self.candidate_seq + 1
                self.investigate_items()
            elif self.candidate in EXCEPT_ITEM :        ## 제외 항목인 경우
                print("exception item : ", self.candidate)
                self.candidate_seq = self.candidate_seq + 1
                self.investigate_items()
            else :
                print("[investigate_items] checking item : ", self.candidate)

                self.kiwoom.dynamicCall("SetInputValue(QString, QString)", "종목코드", self.candidate)
                self.kiwoom.dynamicCall("CommRqData(QString, QString, int, QString)", "GET_iteminfo", "opt10001", 0, "0102")

    def res_iteminfo(self, rqname, trcode, recordname) :
        item_code = self.kiwoom.dynamicCall("GetCommData(QString, QString, int, QString)", trcode, recordname, 0, "종목코드")
        percent = self.kiwoom.dynamicCall("GetCommData(QString, QString, int, QString)", trcode, recordname, 0, "등락율").strip()
        start = int(self.kiwoom.dynamicCall("GetCommData(QString, QString, int, QString)", trcode, recordname, 0, "시가").replace('+', '').replace('-', ''))
        cur_price = int(self.kiwoom.dynamicCall("GetCommData(QString, QString, int, QString)", trcode, recordname, 0, "현재가").replace('+', '').replace('-', ''))

        per_data = float(percent[1:])

        if percent[0] == '-' :                  ## 금일 가격이 전일 종가보다 내려져 있는 경우
            if start >= cur_price :             ## 금일 가격이 음봉일 경우
                print("candidate item CAT 1 : ", item_code, percent, start, cur_price)
                self.kiwoom.dynamicCall("SetInputValue(QString, QString)", "종목코드", self.candidate)
                self.kiwoom.dynamicCall("CommRqData(QString, QString, int, QString)", "CHECK_hoga", "opt10004", 0, "0101")
            else :                              ## 금일 가격이 양봉일 경우
                print("candidate item CAT 2 : ", item_code, percent, start, cur_price)
                self.candidate_seq = self.candidate_seq + 1
                QtTest.QTest.qWait(500)
                self.investigate_items()

        elif percent[0] == '+' or percent[0] == '0':
            print("candidate item CAT 3 : ", item_code, percent)
            self.candidate_seq = self.candidate_seq + 1
            QtTest.QTest.qWait(500)
            self.investigate_items()

    def check_hoga_n_order(self, rqname, trcode, recordname) :
        price_buy = int(self.kiwoom.dynamicCall("GetCommData(QString, QString, int, QString)", trcode, recordname, 0, "매수최우선호가").replace('+', '').replace('-', ''))
        price_sell = int(self.kiwoom.dynamicCall("GetCommData(QString, QString, int, QString)", trcode, recordname, 0, "매도최우선호가").replace('+', '').replace('-', ''))

        if price_sell > UNIT_PRICE_HI_LIM :
            print(self.now(), "[TIMER] [check_hoga_n_order] : 단가 너무 쎔")
            self.candidate_seq = self.candidate_seq + 1
            QtTest.QTest.qWait(500)
            self.investigate_items()

        elif price_sell < UNIT_PRICE_LOW_LIM :
            print(self.now(), "[TIMER] [check_hoga_n_order] : 단가 너무 쌈")
            self.candidate_seq = self.candidate_seq + 1
            QtTest.QTest.qWait(500)
            self.investigate_items()
        
        elif price_sell >= UNIT_PRICE_LOW_LIM and price_sell <= UNIT_PRICE_HI_LIM :
            qty = math.floor(AUTO_BUY_PRICE_LIM / price_sell)
            print(self.now(), "[TIMER] [check_hoga_n_order] : 단가 적당 / ", self.candidate, qty, price_sell)

            temp = {}
            temp['item_code'] = self.candidate
            temp['qty'] = qty
            # temp['qty'] = 1
            temp['price'] = price_sell
            self.req_buy.emit(temp)

    def receive_tr_data(self, screen_no, rqname, trcode, recordname, prev_next, data_len, err_code, msg1, msg2):
        print(self.now(), "[TIMER] [receive_tr_data] : ", rqname)

        if rqname == "CHECK_hoga":
            self.check_hoga_n_order(rqname, trcode, recordname)

        elif rqname == "GET_iteminfo":
            self.res_iteminfo(rqname, trcode, recordname)
            
    @pyqtSlot(int)
    def reply_buy(self, data) :
        print("timer reply buy : ", data)
        if data == 1:                   ## data를 받은 경우
            self.item_checking = 0      ## request 후 구매 완료
            print("timer item_checking unlock")
    
    def now(self) :
        return datetime.datetime.now()

    def func_GET_RepeatCount(self, trcode, rqname):
        ret = self.kiwoom.dynamicCall("GetRepeatCnt(QString, QString)", trcode, rqname)
        return ret           