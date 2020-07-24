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
        self.finder = module_finder.Finder()
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
            mkt_close = now.replace(hour=15, minute=20, second=0)
            am10 = now.replace(hour=10, minute=00, second=0)

            item_finding = now.replace(hour=13, minute=53, second=30)

            c_hour = now.strftime('%H')
            c_min = now.strftime('%M')
            c_sec = now.strftime('%S')

            str_time = c_hour + ':' + c_min + ':' + c_sec
            temp_time['time'] = str_time

            if now >= mkt_open and now < mkt_close :
                temp_time['possible'] = 1
                if now >= am10 and c_sec == "00" :
                    self.refresh_status.emit(1)

                if now >= am10 and c_sec == "00" and self.item_checking == 0 :
                    self.check_slot.emit(1)
            else :
                temp_time['possible'] = 0
            self.cur_time.emit(temp_time)
            test_time = test_time + 1
            time.sleep(1)

    @pyqtSlot(list)
    def res_check_slot(self, data) :
        print("res check slot : ", data)
        self.cur_items = data
        empty = 0

        for i in range(5) :
            if data[i] == 0 :
                empty = empty + 1

        print("empty : ", empty)

        if empty != 0 :
            self.item_checking = 1
            # self.finder.start()
    
    @pyqtSlot(dict)
    def check_candidate(self, data) :
        print("checking candidate")
        print(data)
        empty = data['empty']

        if empty == 1 :     ## item discovery 결과 적정한 item 이 없는 경우
            print("No candidate")
            self.item_checking = 0
        
        elif empty == 0 :   ## 적정 item이 있는 경우
            item_code = data['item_code']
            
            self.candidate_queue = []       ## queue initialize
            self.candidate_queue = data['item_code']    ## fill candidates in queue
            self.candidate_seq = 0          ## first candidate
            self.investigate_items()

            # item_cnt = len(item_code)

            # for i in range(item_cnt) :
            #     self.candidate = item_code[i]
            #     if self.candidate in self.cur_items :
            #         continue
            #     break

            # print("chekcing item info : ", self.candidate)
            # self.kiwoom.dynamicCall("SetInputValue(QString, QString)", "종목코드", self.candidate)
            # self.kiwoom.dynamicCall("CommRqData(QString, QString, int, QString)", "GET_ItemInfo", "opt10001", 0, "0101")
    
    def investigate_items(self) :
        print("investigating items : ", self.candidate_queue)
        print("seq : ", self.candidate_seq)

        if self.candidate_seq >= len(self.candidate_queue) :
            print("candidate seq overflow : Finish Checking")
            self.item_checking = 0
        else :
            self.candidate = self.candidate_queue[self.candidate_seq]

            if self.candidate in self.cur_items :
                self.candidate_seq = self.candidate_seq + 1
                self.investigate_items()
            else :
                print("checking item : ", self.candidate)
                self.kiwoom.dynamicCall("SetInputValue(QString, QString)", "종목코드", self.candidate)
                self.kiwoom.dynamicCall("CommRqData(QString, QString, int, QString)", "GET_hoga", "opt10004", 0, "0101")

    def receive_tr_data(self, screen_no, rqname, trcode, recordname, prev_next, data_len, err_code, msg1, msg2):
        print("[receive_tr_data] ", rqname)

        if rqname == "GET_ItemInfo":
            self.func_GET_ItemInfo(rqname, trcode, recordname)
        if rqname == "GET_hoga":
            self.func_GET_hoga(rqname, trcode, recordname)

    def func_GET_ItemInfo(self, rqname, trcode, recordname) :
        print("timer func_GET_ItemInfo")
        item_code = self.kiwoom.dynamicCall("GetCommData(QString, QString, int, QString)", trcode, recordname, 0, "종목코드")
        name = self.kiwoom.dynamicCall("GetCommData(QString, QString, int, QString)", trcode, recordname, 0, "종목명")
        volume = self.kiwoom.dynamicCall("GetCommData(QString, QString, int, QString)", trcode, recordname, 0, "거래량")
        percent = self.kiwoom.dynamicCall("GetCommData(QString, QString, int, QString)", trcode, recordname, 0, "등락율")
        current_price = self.kiwoom.dynamicCall("GetCommData(QString, QString, int, QString)", trcode, recordname, 0, "현재가")
        current_price = self.kiwoom.dynamicCall("GetCommData(QString, QString, int, QString)", trcode, recordname, 0, "현재가").replace('+', '').replace('-', '').strip()

        self.kiwoom.dynamicCall("SetInputValue(QString, QString)", "종목코드", self.candidate)
        self.kiwoom.dynamicCall("CommRqData(QString, QString, int, QString)", "GET_hoga", "opt10004", 0, "0101")

    def func_GET_hoga(self, rqname, trcode, recordname) :
        print("timer func_GET_hoga : ", self.candidate)
        hoga_buy = int(self.kiwoom.dynamicCall("GetCommData(QString, QString, int, QString)", trcode, recordname, 0, "매수최우선호가").replace('+', '').replace('-', ''))
        hoga_sell = int(self.kiwoom.dynamicCall("GetCommData(QString, QString, int, QString)", trcode, recordname, 0, "매도최우선호가").replace('+', '').replace('-', ''))

        if hoga_sell > UNIT_PRICE_LIMIT :
            print("단가 너무 쎔")
            self.candidate_seq = self.candidate_seq + 1
            self.investigate_items()
        
        elif hoga_sell <= UNIT_PRICE_LIMIT :
            print("단가 적당")
            qty = math.floor(AUTO_BUY_PRICE_LIMIT / hoga_sell)

            print("candidate : ", self.candidate)
            print("단가 : ", hoga_sell)
            print("수량 : ", qty)

            temp = {}
            temp['item_code'] = self.candidate
            temp['qty'] = qty
            temp['buy_price'] = hoga_sell

            self.req_buy.emit(temp)
            self.item_checking = 0