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
import module_finder
from PyQt5.QtWidgets import *
from PyQt5.QAxContainer import *

UNIT_PRICE_HI_LIM = config.UNIT_PRICE_HI_LIM
UNIT_PRICE_LOW_LIM = config.UNIT_PRICE_LOW_LIM
AUTO_BUY_PRICE_LIM = config.AUTO_BUY_PRICE_LIM
ITEM_FINDER_PERCENT = config.ITEM_FINDER_PERCENT
EXCEPT_ITEM = config.EXCEPT_ITEM
SLOT_EMPTY = 0

class Timer(QThread):
    cur_time = pyqtSignal(dict)
    check_slot = pyqtSignal(int)
    refresh_status = pyqtSignal(int)
    req_buy = pyqtSignal(dict)

    def __init__(self):
        super().__init__()
        # self.make_db_table()
        self.item_checking = 0
        self.candidate = ""

        self.waiting_time = 0
        self.waiting_check = 0

        self.finder = module_finder.Finder()
        self.finder.alive.connect(self.finder_alive_checking)
        self.finder.candidate.connect(self.check_candidate)

        self.kiwoom = QAxWidget()
        self.kiwoom.setControl("KHOPENAPI.KHOpenAPICtrl.1")
        self.kiwoom.dynamicCall("CommConnect()")

        self.kiwoom.OnReceiveTrData.connect(self.receive_tr_data)

    def run(self):
        temp_time = {}
        test_time = 0
        while True:
            now = datetime.datetime.now()
            mkt_open = now.replace(hour=9, minute=0, second=0)
            mkt_close = now.replace(hour=15, minute=30, second=0)
            am930 = now.replace(hour=9, minute=30, second=0)
            pm240 = now.replace(hour=14, minute=40, second=0)

            c_hour = now.strftime('%H')
            c_min = now.strftime('%M')
            c_sec = now.strftime('%S')

            str_time = c_hour + ':' + c_min + ':' + c_sec
            temp_time['time'] = str_time

            if now >= mkt_open and now < mkt_close :
                temp_time['possible'] = 1
                if now >= am930 and c_sec == "00" :
                    print(self.now(), "[TIMER] [run] item finding : ", self.waiting_time)
                    self.refresh_status.emit(1)

                if now >= am930 and now<=pm240 and c_sec == "00" and self.item_checking == 0 :
                    self.check_slot.emit(1)
            else :
                temp_time['possible'] = 0
            self.cur_time.emit(temp_time)
            test_time = test_time + 1

            if self.waiting_check == 1 :
                self.waiting_time = self.waiting_time + 1
                if self.waiting_time % 2 == 0 :
                    print("[TIMER] [run] item finding : ", self.waiting_time)

            elif self.waiting_check == 2 :
                self.waiting_time = 0       ## waiting time initialize
                self.waiting_check = 0
                print(self.now(), "[TIMER] [run] item finder alive checking END")
            
            # elif self.waiting_check == 0 :
            #     self.waiting_time = 0       ## waiting time initialize

            if self.waiting_time == 100 :        ## item finding 중 100 이상 응답이 없을 경우
                print(self.now(), "[TIMER] [run] item finder alive checking END - exceed 100")
                self.waiting_time = 0
                self.waiting_check = 0
                self.finder.terminate()         ## 쓰레드 종료
                self.item_checking = 0          ## item checking 해제

                self.finder = module_finder.Finder()        ## 신규 쓰레드 생성
                self.finder.alive.connect(self.finder_alive_checking)
                self.finder.candidate.connect(self.check_candidate)
                # self.finder.start()

            time.sleep(1)

    @pyqtSlot(int)
    def finder_alive_checking(self, data) :
        if data == 1 :      ## item finding is alive
            print(self.now(), "[TIMER] [finder_alive_checking] START")
            self.waiting_check = 1      ## waiting check start
            self.waiting_time = 0
        
        elif data == 2 :    ## item finding finish
            self.waiting_check = 2      ## waiting check stop

    @pyqtSlot(list)
    def res_check_slot(self, data) :
        self.cur_items = data
        empty = 0

        for i in range(5) :
            if data[i] == 0 :
                empty = empty + 1

        print(self.now(), "[TIMER] [res_check_slot] : ", data, "-> empty : ", empty)

        # if empty != 0 :
        if empty > SLOT_EMPTY :
            self.item_checking = 1
            self.finder.start()
    
    @pyqtSlot(dict)
    def check_candidate(self, data) :
        empty = data['empty']

        if empty == 1 :                                     ## item discovery 결과 적정한 item 이 없는 경우
            print(self.now(), "[TIMER] [check_candidate] : NO PROPER CANDIDATE")
            self.item_checking = 0
        
        elif empty == 0 :                                   ## 적정 item이 있는 경우
            self.candidate_queue = []                       ## queue initialize
            self.candidate_queue = data['item_code']        ## fill candidates in queue
            self.candidate_seq = 0                          ## first candidate
            self.investigate_items()
    
    def investigate_items(self) :
        print(self.now(), "[TIMER] [investigate_items] : ", self.candidate_queue, self.candidate_seq)

        if self.candidate_seq >= len(self.candidate_queue) :
            print(self.now(), "[TIMER] [investigate_items] : candidate seq overflow / FINISH")
            self.item_checking = 0
        else :
            self.candidate = self.candidate_queue[self.candidate_seq]

            print("cur items : ", self.cur_items)

            if self.candidate in self.cur_items :
                print("already own item")
                self.candidate_seq = self.candidate_seq + 1
                self.investigate_items()
            elif self.candidate in EXCEPT_ITEM :
                print("exception item choosed : ", self.candidate)
                self.candidate_seq = self.candidate_seq + 1
                self.investigate_items()
            else :
                print(self.now(), "[TIMER] [investigate_items] checking item : ", self.candidate)

                self.kiwoom.dynamicCall("SetInputValue(QString, QString)", "종목코드", self.candidate)
                self.kiwoom.dynamicCall("CommRqData(QString, QString, int, QString)", "GET_iteminfo", "opt10001", 0, "0102")

                # self.kiwoom.dynamicCall("SetInputValue(QString, QString)", "종목코드", self.candidate)
                # self.kiwoom.dynamicCall("CommRqData(QString, QString, int, QString)", "GET_hoga", "opt10004", 0, "0101")

    def res_iteminfo(self, rqname, trcode, recordname) :
        item_code = self.kiwoom.dynamicCall("GetCommData(QString, QString, int, QString)", trcode, recordname, 0, "종목코드")
        name = self.kiwoom.dynamicCall("GetCommData(QString, QString, int, QString)", trcode, recordname, 0, "종목명")
        percent = self.kiwoom.dynamicCall("GetCommData(QString, QString, int, QString)", trcode, recordname, 0, "등락율")

        print("candidate item : ", item_code, name, percent)
        percent = percent.strip()
        per_data = float(percent[1:])

        if percent[0] == '+' and per_data >= ITEM_FINDER_PERCENT :
            print("item finder item 등 + 2.5 이상")
            self.candidate_seq = self.candidate_seq + 1
            self.investigate_items()
        else :
            self.kiwoom.dynamicCall("SetInputValue(QString, QString)", "종목코드", self.candidate)
            self.kiwoom.dynamicCall("CommRqData(QString, QString, int, QString)", "GET_hoga", "opt10004", 0, "0101")

    def receive_tr_data(self, screen_no, rqname, trcode, recordname, prev_next, data_len, err_code, msg1, msg2):
        print(self.now(), "[TIMER] [receive_tr_data] : ", rqname)

        if rqname == "GET_hoga":
            self.func_GET_hoga(rqname, trcode, recordname)

        elif rqname == "GET_iteminfo":
            self.res_iteminfo(rqname, trcode, recordname)

    def func_GET_hoga(self, rqname, trcode, recordname) :
        price_buy = int(self.kiwoom.dynamicCall("GetCommData(QString, QString, int, QString)", trcode, recordname, 0, "매수최우선호가").replace('+', '').replace('-', ''))
        price_sell = int(self.kiwoom.dynamicCall("GetCommData(QString, QString, int, QString)", trcode, recordname, 0, "매도최우선호가").replace('+', '').replace('-', ''))

        if price_sell > UNIT_PRICE_HI_LIM :
            print(self.now(), "[TIMER] [func_GET_hoga] : 단가 너무 쎔")
            self.candidate_seq = self.candidate_seq + 1
            self.investigate_items()

        elif price_sell < UNIT_PRICE_LOW_LIM :
            print(self.now(), "[TIMER] [func_GET_hoga] : 단가 너무 쌈")
            self.candidate_seq = self.candidate_seq + 1
            self.investigate_items()
        
        elif price_sell >= UNIT_PRICE_LOW_LIM and price_sell <= UNIT_PRICE_HI_LIM :
            qty = math.floor(AUTO_BUY_PRICE_LIM / price_sell)

            temp = {}
            temp['item_code'] = self.candidate
            temp['qty'] = qty
            temp['price'] = price_sell

            print(self.now(), "[TIMER] [func_GET_hoga] : 단가 적당 / ", self.candidate, qty, price_sell)

            self.req_buy.emit(temp)
            
    @pyqtSlot(int)
    def reply_buy(self, data) :
        if data == 1:                   ## data를 받은 경우
            self.item_checking = 0      ## request 후 구매 완료
    
    def now(self) :
        return datetime.datetime.now()
