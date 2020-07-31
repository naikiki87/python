import sys
import time
import math
import datetime
import sqlite3
from PyQt5.QtCore import *
from PyQt5 import QtTest, QtCore, QtWidgets
import pandas as pd 
import requests
import threading
from bs4 import BeautifulSoup
import module_finder
from PyQt5.QtWidgets import *
from PyQt5.QAxContainer import *

UNIT_PRICE_LIMIT = 50000
AUTO_BUY_PRICE_LIMIT = 100000

class Timer(QThread):
    cur_time = pyqtSignal(dict)
    new_deal = pyqtSignal(dict)
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
        now = self.now()
        temp_time = {}
        test_time = 0
        while True:
            now = datetime.datetime.now()
            mkt_open = now.replace(hour=9, minute=0, second=0)
            mkt_close = now.replace(hour=15, minute=20, second=0)
            # am10 = now.replace(hour=10, minute=00, second=0)
            am930 = now.replace(hour=9, minute=30, second=0)
            pm230 = now.replace(hour=14, minute=30, second=0)

            item_finding = now.replace(hour=13, minute=53, second=30)

            c_hour = now.strftime('%H')
            c_min = now.strftime('%M')
            c_sec = now.strftime('%S')

            str_time = c_hour + ':' + c_min + ':' + c_sec
            temp_time['time'] = str_time

            if now >= mkt_open and now < mkt_close :
                temp_time['possible'] = 1
                if now >= am930 and c_sec == "00" :
                    self.refresh_status.emit(1)

                if now >= am930 and now<=pm230 and c_sec == "00" and self.item_checking == 0 :
                    self.check_slot.emit(1)
            else :
                temp_time['possible'] = 0
            self.cur_time.emit(temp_time)
            test_time = test_time + 1

            if self.waiting_check == 1 :
                self.waiting_time = self.waiting_time + 1
                print(now, "[TIMER]", "item finding waiting : ", self.waiting_time)
            
            elif self.waiting_check == 0 :
                self.waiting_time = 0       ## waiting time initialize
                print(now, "[TIMER]", "item finder alive checking end")

            if self.waiting_time == 60 :        ## item finding 중 100 이상 응답이 없을 경우
                self.finder.terminate()         ## 쓰레드 종료
                self.item_checking = 0          ## item checking 해제

                self.finder = module_finder.Finder()        ## 신규 쓰레드 생성
                self.finder.alive.connect(self.finder_alive_checking)
                self.finder.candidate.connect(self.check_candidate)

            time.sleep(1)

    @pyqtSlot(int)
    def finder_alive_checking(self, data) :
        now = self.now()
        print(now, "[TIMER]", "finder alive checking")

        if data == 1 :      ## item finding is alive
            self.waiting_check = 1      ## waiting check start
            self.waiting_time = 0
        
        elif data == 2 :    ## item finding finish
            self.waiting_check = 0      ## waiting check stop

    @pyqtSlot(list)
    def res_check_slot(self, data) :
        now = self.now()
        print(now, "[TIMER]", "res check slot : ", data)
        self.cur_items = data
        empty = 0

        for i in range(5) :
            if data[i] == 0 :
                empty = empty + 1

        print(now, "[TIMER]", "empty : ", empty)

        if empty != 0 :
            self.item_checking = 1
            self.finder.start()
    
    @pyqtSlot(dict)
    def check_candidate(self, data) :
        now = self.now()
        print(now, "[TIMER]", "checking candidate")
        print(now, "[TIMER]", data)
        empty = data['empty']

        if empty == 1 :     ## item discovery 결과 적정한 item 이 없는 경우
            print(now, "[TIMER]", "No candidate")
            self.item_checking = 0
        
        elif empty == 0 :   ## 적정 item이 있는 경우
            item_code = data['item_code']
            
            self.candidate_queue = []       ## queue initialize
            self.candidate_queue = data['item_code']    ## fill candidates in queue
            self.candidate_seq = 0          ## first candidate
            self.investigate_items()
    
    def investigate_items(self) :
        now = self.now()
        print(now, "[TIMER]", "investigating items : ", self.candidate_queue)
        print(now, "[TIMER]", "seq : ", self.candidate_seq)

        if self.candidate_seq >= len(self.candidate_queue) :
            print(now, "[TIMER]", "candidate seq overflow : Finish Checking")
            self.item_checking = 0
        else :
            self.candidate = self.candidate_queue[self.candidate_seq]

            if self.candidate in self.cur_items :
                self.candidate_seq = self.candidate_seq + 1
                self.investigate_items()
            else :
                print(now, "[TIMER]", "checking item : ", self.candidate)
                self.kiwoom.dynamicCall("SetInputValue(QString, QString)", "종목코드", self.candidate)
                self.kiwoom.dynamicCall("CommRqData(QString, QString, int, QString)", "GET_hoga", "opt10004", 0, "0101")

    def receive_tr_data(self, screen_no, rqname, trcode, recordname, prev_next, data_len, err_code, msg1, msg2):
        now = self.now()
        print(now, "[TIMER]", "[receive_tr_data] ", rqname)

        if rqname == "GET_ItemInfo":
            self.func_GET_ItemInfo(rqname, trcode, recordname)
        if rqname == "GET_hoga":
            self.func_GET_hoga(rqname, trcode, recordname)

    def func_GET_ItemInfo(self, rqname, trcode, recordname) :
        now = self.now()
        print(now, "[TIMER]", "timer func_GET_ItemInfo")
        item_code = self.kiwoom.dynamicCall("GetCommData(QString, QString, int, QString)", trcode, recordname, 0, "종목코드")
        name = self.kiwoom.dynamicCall("GetCommData(QString, QString, int, QString)", trcode, recordname, 0, "종목명")
        volume = self.kiwoom.dynamicCall("GetCommData(QString, QString, int, QString)", trcode, recordname, 0, "거래량")
        percent = self.kiwoom.dynamicCall("GetCommData(QString, QString, int, QString)", trcode, recordname, 0, "등락율")
        current_price = self.kiwoom.dynamicCall("GetCommData(QString, QString, int, QString)", trcode, recordname, 0, "현재가")
        current_price = self.kiwoom.dynamicCall("GetCommData(QString, QString, int, QString)", trcode, recordname, 0, "현재가").replace('+', '').replace('-', '').strip()

        self.kiwoom.dynamicCall("SetInputValue(QString, QString)", "종목코드", self.candidate)
        self.kiwoom.dynamicCall("CommRqData(QString, QString, int, QString)", "GET_hoga", "opt10004", 0, "0101")

    def func_GET_hoga(self, rqname, trcode, recordname) :
        now = self.now()
        print(now, "[TIMER]", "timer func_GET_hoga : ", self.candidate)
        price_buy = int(self.kiwoom.dynamicCall("GetCommData(QString, QString, int, QString)", trcode, recordname, 0, "매수최우선호가").replace('+', '').replace('-', ''))
        price_sell = int(self.kiwoom.dynamicCall("GetCommData(QString, QString, int, QString)", trcode, recordname, 0, "매도최우선호가").replace('+', '').replace('-', ''))

        if price_sell > UNIT_PRICE_LIMIT :
            print(now, "[TIMER]", "단가 너무 쎔")
            self.candidate_seq = self.candidate_seq + 1
            self.investigate_items()
        
        elif price_sell <= UNIT_PRICE_LIMIT :
            print(now, "[TIMER]", "단가 적당")
            qty = math.floor(AUTO_BUY_PRICE_LIMIT / price_sell)

            print(now, "[TIMER]", "candidate : ", self.candidate)
            print(now, "[TIMER]", "단가 : ", price_sell)
            print(now, "[TIMER]", "수량 : ", qty)

            temp = {}
            temp['item_code'] = self.candidate
            temp['qty'] = qty
            temp['price'] = price_sell

            self.req_buy.emit(temp)

    @pyqtSlot(int)
    def reply_buy(self, data) :
        now = self.now()
        if data == 1:
            self.item_checking = 0      ## request 후 구매 완료
    
    def now(self) :
        return datetime.datetime.now()
