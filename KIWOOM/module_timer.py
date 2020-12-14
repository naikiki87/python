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
ITEM_FINDER_PERCENT_LOW = config.ITEM_FINDER_PERCENT_LOW
EXCEPT_ITEM = config.EXCEPT_ITEM
DELAY_SEC = config.DELAY_SEC
SLOT_EMPTY = config.NUM_SLOT - config.SLOT_RUN


print("timer SLOT EMPTY : ", SLOT_EMPTY)

class Timer(QThread):
    cur_time = pyqtSignal(dict)
    check_slot = pyqtSignal(int)
    refresh_status = pyqtSignal(int)
    req_buy = pyqtSignal(dict)
    release_paused = pyqtSignal(int)
    check_real = pyqtSignal(int)
    req_slot = pyqtSignal(int)
    sig_main_check_jumun = pyqtSignal(int)
    timer_connected = pyqtSignal(int)

    def __init__(self):
        super().__init__()
        self.timer_on = 0
        self.paused = [0,0,0,0,0]
        self.paused_remain_sec = [0,0,0,0,0]

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

        self.kiwoom.OnEventConnect.connect(self.event_connect)
        self.kiwoom.OnReceiveTrData.connect(self.receive_tr_data)

        self.list_surprise = []
        self.list_surprise_vol = []

        self.pagenum = 1050

    def event_connect(self, err_code):
        if err_code == 0 :
            self.timer_on = 1
            print("timer connect")
            self.timer_connected.emit(1)

    def run(self):
        temp_time = {}
        while True:
            if self.timer_on == 1 :
                now = datetime.datetime.now()
                mkt_open = now.replace(hour=9, minute=0, second=0)
                mkt_close = now.replace(hour=15, minute=30, second=0)
                am920 = now.replace(hour=9, minute=20, second=0)
                pm230 = now.replace(hour=14, minute=30, second=0)
                pm250 = now.replace(hour=14, minute=50, second=0)
                pm320 = now.replace(hour=15, minute=20, second=0)

                c_hour = now.strftime('%H')
                c_min = now.strftime('%M')
                c_sec = now.strftime('%S')

                str_time = c_hour + ':' + c_min + ':' + c_sec
                temp_time['time'] = str_time

                if now >= mkt_open and now < mkt_close :
                    temp_time['possible'] = 1
                    if now >= am920 and c_sec == "00" :
                        self.refresh_status.emit(1)

                    if now >= am920 and now<=pm250 and c_sec == "30" and self.item_checking == 0 :
                        self.check_slot.emit(1)
                    if c_sec == "05" :
                        self.check_real.emit(1)
                    
                    if now >= am920 and now<=pm320 and c_sec == "15" :
                        self.sig_main_check_jumun.emit(1)
                        
                    # if c_sec == "10":
                    #     print("find surprise vol : ", self.pagenum)
                        # self.check_surprise_vol()

                    if now <= am920 :
                        temp_time['timezone'] = 1
                    elif now > am920 and now <= pm230 :
                        temp_time['timezone'] = 2
                    elif now > pm230 :
                        temp_time['timezone'] = 2
                        
                else :
                    temp_time['possible'] = 0
                    temp_time['timezone'] = 0
                # print("[timer] Timezone : ", temp_time['timezone'])
                self.cur_time.emit(temp_time)       ## 현재시각 및 market status send


                if self.waiting_check == 1 :
                    self.waiting_time = self.waiting_time + 1
                    if self.waiting_time % 2 == 0 :
                        print("[TIMER] [run] item finding : ", self.waiting_time)

                    if self.waiting_time == 100 :        ## item finding 중 100 이상 응답이 없을 경우
                        print("[TIMER] [run] item finder alive checking END - exceed 100")
                        self.waiting_time = 0
                        self.waiting_check = 0
                        self.finder.terminate()         ## 쓰레드 종료
                        self.item_checking = 0          ## item checking 해제

                        self.finder = module_finder.Finder()        ## 신규 쓰레드 생성
                        self.finder.alive.connect(self.finder_alive_checking)
                        self.finder.candidate.connect(self.check_candidate)

                elif self.waiting_check == 2 :
                    self.waiting_time = 0       ## waiting time initialize
                    self.waiting_check = 0
                    print("[TIMER] [run] item finder alive checking END")

                for i in range(5) :
                    if self.paused[i] == 1 :
                        if self.paused_remain_sec[i] != 0 :
                            self.paused_remain_sec[i] = self.paused_remain_sec[i] - 1
                        elif self.paused_remain_sec[i] == 0 :
                            self.paused[i] = 0
                            self.release_paused.emit(i)

            time.sleep(1)

    # def check_surprise_vol(self) :
    #     print("[timer] check surprise vol")
    #     try :
    #         self.list_surprise_vol = []

    #         self.pagenum = self.pagenum + 1

    #         print("1")

    #         self.kiwoom.dynamicCall("SetInputValue(QString, QString)", "시장구분", "000")
    #         self.kiwoom.dynamicCall("SetInputValue(QString, QString)", "정렬구분", 1)
    #         self.kiwoom.dynamicCall("SetInputValue(QString, QString)", "시간구분", 1)
    #         self.kiwoom.dynamicCall("SetInputValue(QString, QString)", "거래량구분", 500)
    #         self.kiwoom.dynamicCall("SetInputValue(QString, QString)", "시간", 1)
    #         self.kiwoom.dynamicCall("CommRqData(QString, QString, int, QString)", "GET_surprise_vol", "OPT10023", 0, str(self.pagenum))
    #         print("send order surprise vol")
    #     except :
    #         pass

    # def func_SHOW_surprise_vol(self, rqname, trcode, recordname):
    #     print("func show surprise volume")
    #     data_cnt = int(self.func_GET_RepeatCount(trcode, rqname))
    #     print("data cnt : ", data_cnt)
    #     for i in range(15) :
    #         try :
    #             item_code = self.kiwoom.dynamicCall("GetCommData(QString, QString, int, QString)", trcode, recordname, i, "종목코드").strip()
    #             item_name = self.kiwoom.dynamicCall("GetCommData(QString, QString, int, QString)", trcode, recordname, i, "종목명").strip()
    #             price_cur = self.kiwoom.dynamicCall("GetCommData(QString, QString, int, QString)", trcode, recordname, i, "현재가").replace('+', '').replace('-', '').strip()
    #             percent = self.kiwoom.dynamicCall("GetCommData(QString, QString, int, QString)", trcode, recordname, i, "등락률")
    #             vol_prev = self.kiwoom.dynamicCall("GetCommData(QString, QString, int, QString)", trcode, recordname, i, "이전거래량")
    #             vol_cur = self.kiwoom.dynamicCall("GetCommData(QString, QString, int, QString)", trcode, recordname, i, "현재거래량")
    #             amount_surprise = self.kiwoom.dynamicCall("GetCommData(QString, QString, int, QString)", trcode, recordname, i, "급증량")
    #             percent_surprise = self.kiwoom.dynamicCall("GetCommData(QString, QString, int, QString)", trcode, recordname, i, "급증률")

    #             # print(i, item_code, item_name, price_cur, percent, vol_prev, vol_cur, amount_surprise, percent_surprise)

    #             self.list_surprise_vol.append(item_code)

    #         except :
    #             pass

    #     print("surprise vol : ", self.list_surprise_vol)


    # def check_surprise(self) :
    #     print("[timer] check surprise")
    #     self.list_surprise = []
    #     self.kiwoom.dynamicCall("SetInputValue(QString, QString)", "시장구분", "000")
    #     self.kiwoom.dynamicCall("SetInputValue(QString, QString)", "등락구분", 1)
    #     self.kiwoom.dynamicCall("SetInputValue(QString, QString)", "시간구분", 1)
    #     self.kiwoom.dynamicCall("SetInputValue(QString, QString)", "시간", 1)
    #     self.kiwoom.dynamicCall("CommRqData(QString, QString, int, QString)", "GET_surprise", "opt10019", 0, "0101")

    # def func_SHOW_surprise(self, rqname, trcode, recordname):
    #     print("func show surprise")
    #     data_cnt = int(self.func_GET_RepeatCount(trcode, rqname))

    #     print("data cnt : ", data_cnt)
    #     for i in range(data_cnt) :
    #         try :
    #             item_code = self.kiwoom.dynamicCall("GetCommData(QString, QString, int, QString)", trcode, recordname, i, "종목코드").strip()
    #             # item_div = self.kiwoom.dynamicCall("GetCommData(QString, QString, int, QString)", trcode, recordname, i, "종목분류").strip()
    #             # item_name = self.kiwoom.dynamicCall("GetCommData(QString, QString, int, QString)", trcode, recordname, i, "종목명")
    #             # before_flag = self.kiwoom.dynamicCall("GetCommData(QString, QString, int, QString)", trcode, recordname, i, "전일대비기호")
    #             # before = self.kiwoom.dynamicCall("GetCommData(QString, QString, int, QString)", trcode, recordname, i, "전일대비")
    #             # percent = self.kiwoom.dynamicCall("GetCommData(QString, QString, int, QString)", trcode, recordname, i, "등락률")
    #             # price_axis = self.kiwoom.dynamicCall("GetCommData(QString, QString, int, QString)", trcode, recordname, i, "기준가")
    #             # price_cur = self.kiwoom.dynamicCall("GetCommData(QString, QString, int, QString)", trcode, recordname, i, "현재가")
    #             # volume = self.kiwoom.dynamicCall("GetCommData(QString, QString, int, QString)", trcode, recordname, i, "거래량")
    #             # percent_surprise = self.kiwoom.dynamicCall("GetCommData(QString, QString, int, QString)", trcode, recordname, i, "급등률")

    #             # print(i, item_code, item_div, item_name, before_flag, before, percent, price_axis, price_cur, volume, percent_surprise)

    #             self.list_surprise.append(item_code)

    #         except :
    #             pass
    
    @pyqtSlot(list)
    def jumun_check(self, data):
        print("timer jumun check : ", data)

        conn = sqlite3.connect("item_status.db")
        cur = conn.cursor()
        sql = "select code from STATUS where ordered=1"
        cur.execute(sql)
        rows = cur.fetchall()
        conn.close()

        print("paused : ", self.paused)

        for i in range(len(rows)) :
            if rows[i][0] in data :
                print(rows[i][0], "is in cur items")

    @pyqtSlot(int)
    def rcv_paused(self, data) :
        self.paused[data] = 1
        self.paused_remain_sec[data] = DELAY_SEC

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

        print(self.now(), "[TIMER] [res_check_slot] empty : ", empty)

        if empty > SLOT_EMPTY :
            self.item_checking = 1              ## checking 중임을 표시
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

    def res_iteminfo(self, rqname, trcode, recordname) :
        item_code = self.kiwoom.dynamicCall("GetCommData(QString, QString, int, QString)", trcode, recordname, 0, "종목코드")
        name = self.kiwoom.dynamicCall("GetCommData(QString, QString, int, QString)", trcode, recordname, 0, "종목명")
        percent = self.kiwoom.dynamicCall("GetCommData(QString, QString, int, QString)", trcode, recordname, 0, "등락율")

        print("candidate item : ", item_code, name, percent)
        percent = percent.strip()
        per_data = float(percent[1:])

        if percent[0] == '+' and per_data >= ITEM_FINDER_PERCENT :
            print("item finder item 등 " + str(ITEM_FINDER_PERCENT) + "이상")
            self.candidate_seq = self.candidate_seq + 1
            self.investigate_items()
        elif percent[0] == '-' and per_data <= ITEM_FINDER_PERCENT_LOW :
            print("item finder item 낙 " + str(ITEMFINDER_PERCENT_LOW) + "이하")
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

        # elif rqname == "GET_surprise":
        #     self.func_SHOW_surprise(rqname, trcode, recordname)

        # elif rqname == "GET_surprise_vol":
        #     self.func_SHOW_surprise_vol(rqname, trcode, recordname)

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

    def func_GET_RepeatCount(self, trcode, rqname):
        ret = self.kiwoom.dynamicCall("GetRepeatCnt(QString, QString)", trcode, rqname)
        return ret           
