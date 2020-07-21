import sys
import time
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

SHOW_SCALE = 5
VOL_FIN_PAGE = 3    # 평균 volume을 구할 표본 수 -> 1 당 10일치
STDEV_LIMIT = 0.25
VOL_AVERAGE = 1000000    # 평균 volume filtering 하한치
MKT_SUM_LIMIT = 3000

class Timer(QThread):
    cur_time = pyqtSignal(dict)
    new_deal = pyqtSignal(dict)
    check_slot = pyqtSignal(int)
    refresh_status = pyqtSignal(int)

    def __init__(self):
        super().__init__()
        # self.make_db_table()
        self.item_checking = 0
        self.finder = module_finder.Finder()
        self.finder.candidate.connect(self.check_candidate)

        self.kiwoom = QAxWidget()
        self.kiwoom.setControl("KHOPENAPI.KHOpenAPICtrl.1")
        self.kiwoom.dynamicCall("CommConnect()")

        # self.kiwoom.OnReceiveTrData.connect(self.receive_tr_data)

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
                if now >= am10 and c_sec == "00" and self.item_checking == 0 :
                    self.check_slot.emit(1)
            self.cur_time.emit(temp_time)
            test_time = test_time + 1
            time.sleep(1)

    @pyqtSlot(int)
    def res_check_slot(self, data) :
        print("res check slot : ", data)
        if data != 0 :
            self.item_checking = 1
            # self.finder.start()
    
    @pyqtSlot(dict)
    def check_candidate(self, data) :
        print("checking candidate")
        print(data)
        empty = data['empty']

        if empty == 1 :     ## item discovery 결과 적정한 item 이 없는 경우
            self.item_checking = 0
        
        elif empty == 0 :   ## 적정 item이 있는 경우
            item_code = data['item_code']
            recommend = item_code[0]

            print("Checking : ", recommend)
    
    # @pyqtSlot(int)
    # def item_check_complete(self, data) :
    #     print("item check complete")
    #     self.item_checking = 0