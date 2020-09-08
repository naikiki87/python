import sys
import sqlite3
import time
import math
import pandas as pd
import datetime
import config
from time import localtime, strftime
from PyQt5.QtWidgets import *
from PyQt5.QAxContainer import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5 import QtTest, QtCore, QtWidgets, uic, QtGui
import module_timer
import module_worker

form_class = uic.loadUiType("interface.ui")[0]

ACCOUNT = config.ACCOUNT
PASSWORD = config.PASSWORD
NUM_SLOT = config.NUM_SLOT
SUMMARY_COL_CNT = config.SUMMARY_COL_CNT

class Kiwoom(QMainWindow, form_class):
    test_dict0 = pyqtSignal(dict)
    test_dict1 = pyqtSignal(dict)
    test_dict2 = pyqtSignal(dict)
    test_dict3 = pyqtSignal(dict)
    test_dict4 = pyqtSignal(dict)
    che_dict = pyqtSignal(dict)
    res_check_slot = pyqtSignal(list)
    reply_buy = pyqtSignal(int)

    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.kiwoom = QAxWidget()
        self.kiwoom.setControl("KHOPENAPI.KHOpenAPICtrl.1")

        self.kiwoom.dynamicCall("CommConnect()")        ## aloha
        
        self.kiwoom.OnEventConnect.connect(self.event_connect)
        self.kiwoom.OnReceiveTrData.connect(self.receive_tr_data)
        self.kiwoom.OnReceiveRealData.connect(self.receive_real_data)
        self.kiwoom.OnReceiveChejanData.connect(self.func_RECEIVE_Chejan_data)

        self.init_ENV()

    def init_ENV(self) :
        ## flag setting
        self.item_finder_req = 0
        self.check_jumun_times = 0
        self.check_jan = []
        for i in range(5) :
            self.check_jan.append([0,0,0,0])
        self.check_jumun = []
        for i in range(5) :
            self.check_jumun.append(['',0,0,0,0])
        self.check_jumun_2 = ['',0,0,0,0]
        self.send_data = 1
        self.buying_item = 0
        self.input_show_status.setText("STOP")
        self.possible_time = 0
        self.reset_time = 1000
        self.set_deposit = 0
        self.cnt_thread = 0
        self.item_slot = [0, 0, 0, 0, 0]
        self.reset_slot = [0, 0, 0, 0, 0]
        self.list_th_connected = [0, 0, 0, 0, 0]
        self.cnt_call_hoga = 0
        self.cnt_tab_history = 0
        self.flag_HistoryData_Auto = 0
        self.stay_print_time = {}
        self.flag_lock_init = 0
        self.flag_lock = {}

        self.func_SET_db_table()        # db table 생성
        self.df_history = pd.DataFrame(columns = ['time', 'type', 'T_ID', 'Code', 'Name', 'Qty', 'Price', 'Req_ID'])
        self.df_ordering = pd.DataFrame(columns = ['deal_type', 'order_id', 'order_time', 'item_code', 'item_name', 'order_amount', 'trade_amount', 'remained'])

        ## button 동작 binding
        self.btn_ITEM_LOOKUP.clicked.connect(self.func_GET_ItemInfo)
        self.btn_BUY.clicked.connect(self.func_ORDER_BUY)
        self.btn_SELL.clicked.connect(self.func_ORDER_SELL)
        self.btn_TEST.clicked.connect(self.btn_test)
        self.btn_TEST_2.clicked.connect(self.btn_test_2)
        self.btn_START.clicked.connect(self.order_start)
        self.btn_STOP.clicked.connect(self.order_stop)
        self.btn_HISTORY.clicked.connect(self.func_GET_TradeHistory)
        self.btn_dailyprofit.clicked.connect(lambda: self.func_GET_DailyProfit(1))

        ## table setting
        self.func_SET_tableSUMMARY()        # monitoring table
        self.func_SET_tableHISTORY()        # history table
        self.func_SET_tableORDER()          # order 현황 table
        self.func_SET_table_dailyprofit()   # dailyprofit table

    @pyqtSlot(dict)
    def update_times(self, data) :
        self.text_edit4.setText(data['time'])
        self.possible_time = data['possible']
    @pyqtSlot(dict)
    def rp_dict(self, data):
        ordered = data['ordered']
        if ordered == 1 :
            self.table_summary.item(data['seq'], 0).setBackground(QtGui.QColor(0,255,0))
        elif ordered == 2 :
            self.table_summary.item(data['seq'], 0).setBackground(QtGui.QColor(255,255,255))
        elif ordered == 0 :
            self.table_summary.item(data['seq'], 0).setBackground(QtGui.QColor(255,255,255))
        
            self.func_SET_TableData(1, data['seq'], 4, str(data['cur_price']), 0)
            self.func_SET_TableData(1, data['seq'], 5, str(data['price_sell']), 0)
            self.func_SET_TableData(1, data['seq'], 6, str(data['price_buy']), 0)
            self.func_SET_TableData(1, data['seq'], 7, str(data['total_purchase']), 0)
            self.func_SET_TableData(1, data['seq'], 8, str(data['total_evaluation']), 0)
            self.func_SET_TableData(1, data['seq'], 9, str(data['temp_total']), 0)
            self.func_SET_TableData(1, data['seq'], 10, str(data['total_fee']), 0)
            self.func_SET_TableData(1, data['seq'], 11, str(data['total_sum']), 0)
            if data['percent'] > 0 :
                self.func_SET_TableData(1, data['seq'], 12, str(data['percent']), 1)
            elif data['percent'] < 0 :
                self.func_SET_TableData(1, data['seq'], 12, str(data['percent']), 2)
            elif data['percent'] == 0 :
                self.func_SET_TableData(1, data['seq'], 12, str(data['percent']), 0)
            self.func_SET_TableData(1, data['seq'], 13, str(data['step']), 0)
            self.func_SET_TableData(1, data['seq'], 14, str(data['high']), 0)
            self.func_SET_TableData(1, data['seq'], 15, str(data['chegang']), 0)

    @pyqtSlot(int)
    def th_connected(self, data) :
        print(self.now(), "[MAIN] [th_connected] : ", data)
        self.list_th_connected[self.th_seq] = data

    def now(self) :
        return datetime.datetime.now()

    def btn_test(self) :
        print(self.now(), "[MAIN]", "btn test")
        self.worker0.temptest("007460")

    @pyqtSlot(dict)
    def rq_order(self, data) :
        buy_or_sell = data['type']
        item_code = data['item_code']
        qty = data['qty']
        price = data['price']
        print(self.now(), "[MAIN] [rq order] : ", buy_or_sell, item_code, qty, price)

        if buy_or_sell == 0 :  ## BUY
            slot = self.which_thread(item_code)[1]
            order_type = data['order_type']

            self.check_jan[slot] = [0, 0, 0, 0]
            self.check_jan[slot][0] = item_code
            self.check_jan[slot][1] = qty
            self.check_jan[slot][2] = price
            self.check_jan[slot][3] = order_type

            if self.check_jan[slot][0] != 0 and self.check_jan[slot][1] != 0 and self.check_jan[slot][2] != 0 and self.check_jan[slot][3] != 0:
                rq_name = str(item_code) + str(slot) + "jan_check"

                self.kiwoom.dynamicCall("SetInputValue(QString, QString)", "종목코드", item_code)
                self.kiwoom.dynamicCall("CommRqData(QString, QString, int, QString)", rq_name, "opt10004", 0, "0101")
        
        elif buy_or_sell == 1 :  ## SELL
            self.ORDER_SELL(item_code, qty, price)

    def result_get_hoga(self, rqname, trcode, recordname, item_code, item_slot) :
        slot = int(item_slot)
        if item_code == self.check_jan[slot][0] :
            jan_sell = self.kiwoom.dynamicCall("GetCommData(QString, QString, int, QString)", trcode, recordname, 0, "매도최우선잔량").replace('+', '').replace('-', '').strip()
            print("A : ", int(self.check_jan[slot][1]))
            print("B : ", int(jan_sell))
            if int(self.check_jan[slot][1]) <= int(jan_sell) :
                print(self.now(), "[MAIN] [result_get_hoga] jan amount ENOUGH : ", jan_sell)
                self.ORDER_BUY(item_code, self.check_jan[slot][1], self.check_jan[slot][2], self.check_jan[slot][3])
            else :
                print(self.now(), "[MAIN] [result_get_hoga] jan amount NOT ENOUGH : ", jan_sell)

                if slot == 0 :
                    self.worker0.not_ordered(item_code)
                elif slot == 1 :
                    self.worker1.not_ordered(item_code)
                elif slot == 2 :
                    self.worker2.not_ordered(item_code)
                elif slot == 3 :
                    self.worker3.not_ordered(item_code)
                elif slot == 4 :
                    self.worker4.not_ordered(item_code)

                # che_dict = {}
                # che_dict['res'] = 0
                # che_dict['th_num'] = slot
                # che_dict['item_code'] = item_code
                # self.che_dict.emit(che_dict)            ## worker에 통지 및 데이터 삭제

                if self.check_jan[slot][3] == 9 :       ## item find를 통해 신규 find인 경우
                    self.item_slot[slot] = 0            ## slot 해제
                    self.item_finder_req = 0
                    self.reply_buy.emit(1)                  # item finder 재 기동
        
    def btn_test_2(self):
        print(self.now(), "[MAIN]", "btn test2")
        self.SetRealRemove("ALL", "005930")        ## 실시간 데이터 감시 해제

    def DELETE_Table_Summary_item(self, slot) :
        try :
            for i in range(SUMMARY_COL_CNT) :
                self.func_SET_TableData(1, slot, i, "", 0)

            return 0

        except :
            self.DELETE_Table_Summary_item(slot)        ## recursive call
    
    def create_thread(self) :
        timestamp = self.func_GET_CurrentTime()
        self.text_edit.append(timestamp + "CREATE THREADS")
        ## 1st        
        self.th_seq = 0
        self.worker0 = module_worker.Worker(0)
        self.worker0.th_con.connect(self.th_connected)
        self.test_dict0.connect(self.worker0.dict_from_main)
        self.che_dict.connect(self.worker0.che_result)
        self.worker0.trans_dict.connect(self.rp_dict)
        self.worker0.rq_order.connect(self.rq_order)
        self.worker0.start()
        while True :
            if self.list_th_connected[self.th_seq] == 1:
                timestamp = self.func_GET_CurrentTime()
                self.text_edit.append(timestamp + "THREAD 1 CREATED")
                break
            QtTest.QTest.qWait(100)
        ## 2nd
        self.th_seq = 1
        self.worker1 = module_worker.Worker(1)
        self.worker1.th_con.connect(self.th_connected)
        self.test_dict1.connect(self.worker1.dict_from_main)
        self.che_dict.connect(self.worker1.che_result)
        self.worker1.trans_dict.connect(self.rp_dict)
        self.worker1.rq_order.connect(self.rq_order)
        self.worker1.start()
        while True :
            if self.list_th_connected[self.th_seq] == 1:
                timestamp = self.func_GET_CurrentTime()
                self.text_edit.append(timestamp + "THREAD 2 CREATED")
                break
            QtTest.QTest.qWait(100)
        ## 3rd
        self.th_seq = 2
        self.worker2 = module_worker.Worker(2)
        self.worker2.th_con.connect(self.th_connected)
        self.test_dict2.connect(self.worker2.dict_from_main)
        self.che_dict.connect(self.worker2.che_result)
        self.worker2.trans_dict.connect(self.rp_dict)
        self.worker2.rq_order.connect(self.rq_order)
        self.worker2.start()
        while True :
            if self.list_th_connected[self.th_seq] == 1:
                timestamp = self.func_GET_CurrentTime()
                self.text_edit.append(timestamp + "THREAD 3 CREATED")
                break
            QtTest.QTest.qWait(100)
        ## 4th
        self.th_seq = 3
        self.worker3 = module_worker.Worker(3)
        self.worker3.th_con.connect(self.th_connected)
        self.test_dict3.connect(self.worker3.dict_from_main)
        self.che_dict.connect(self.worker3.che_result)
        self.worker3.trans_dict.connect(self.rp_dict)
        self.worker3.rq_order.connect(self.rq_order)
        self.worker3.start()
        while True :
            if self.list_th_connected[self.th_seq] == 1:
                timestamp = self.func_GET_CurrentTime()
                self.text_edit.append(timestamp + "THREAD 4 CREATED")
                break
            QtTest.QTest.qWait(100)

        ## 5th
        self.th_seq = 4
        self.worker4 = module_worker.Worker(4)
        self.worker4.th_con.connect(self.th_connected)
        self.test_dict4.connect(self.worker4.dict_from_main)
        self.che_dict.connect(self.worker4.che_result)
        self.worker4.trans_dict.connect(self.rp_dict)
        self.worker4.rq_order.connect(self.rq_order)
        self.worker4.start()
        while True :
            if self.list_th_connected[self.th_seq] == 1:
                timestamp = self.func_GET_CurrentTime()
                self.text_edit.append(timestamp + "THREAD 5 CREATED")
                break
            QtTest.QTest.qWait(100)
        
        return 0
    def order_start(self) :
        try :
            self.send_data = 1
            self.input_show_status.setText("RUNNING")
        except Exception as e : 
            timestamp = self.func_GET_CurrentTime()
            self.text_edit.append(timestamp + str(e))
        self.load_etc_data()
    def order_stop(self) :
        try :
            self.send_data = 0
            self.input_show_status.setText("STOP")
        except Exception as e : 
            timestamp = self.func_GET_CurrentTime()
            self.text_edit.append(timestamp + str(e))
        self.load_etc_data()
    def func_start_check(self) :
        self.load_etc_data()
        if self.create_thread() == 0 :              ## thread creation
            self.table_summary.clearContents()      ## table clear
            acc_no = ACCOUNT
            acc_pw = PASSWORD
            self.kiwoom.dynamicCall("SetInputValue(QString, QString)", "계좌번호", acc_no)
            self.kiwoom.dynamicCall("SetInputValue(QString, QString)", "비밀번호", acc_pw)
            self.kiwoom.dynamicCall("CommRqData(QString, QString, int, QString)", "SETTING", "opw00018", 0, "0101")
    def func_SET_Items(self, rqname, trcode, recordname):
        # print(self.now(), "[MAIN] [func_SET_Items]")
        self.item_count = int(self.func_GET_RepeatCount(trcode, rqname))

        # print(self.now(), "[MAIN] [func_SET_Items] Code Sync START")
        db_codes = self.func_GET_db_item(0, 0)
        # print(now, "[MAIN]", "[CODE SYNC] DB CODES : ", db_codes)

        for i in range(self.item_count) :
            try :
                item_code = self.kiwoom.dynamicCall("GetCommData(QString, QString, int, QString)", trcode, recordname, i, "종목번호").replace('A', '').strip()
                db_codes.remove(item_code)
            except :
                pass
        # print(now, "[MAIN]", "[CODE SYNC] Code Sync Remains : ", db_codes)

        for i in range(len(db_codes)) :
            self.func_DELETE_db_item(db_codes[i])
        # print(now, "[MAIN] [func_SET_Items] Code Sync REMOVE COMPLETE")

        for i in range(self.item_count) :
            try :
                item_code = self.kiwoom.dynamicCall("GetCommData(QString, QString, int, QString)", trcode, recordname, i, "종목번호").replace('A', '').strip()
                step = self.func_GET_db_item(item_code, 1)

                if step == "none" :
                    self.func_INSERT_db_item(item_code, 0, 0, 0, 0)
                    # print(now, "[MAIN]", "[CODE SYNC] Code is not in DB - Item Initialized : ", item_code)
            except :
                pass
        # print(now, "[MAIN]", "[CODE SYNC] Code Sync - Fill Lack Item Complete")
        # print(self.now(), "[MAIN] [func_SET_Items] Code Sync END")

        # time.sleep(2)
        QtTest.QTest.qWait(1000)

        for i in range(self.item_count) :
            item_code = self.kiwoom.dynamicCall("GetCommData(QString, QString, int, QString)", trcode, recordname, i, "종목번호").replace('A', '').strip()
            item_name = self.kiwoom.dynamicCall("GetCommData(QString, QString, int, QString)", trcode, recordname, i, "종목명").strip()
            owncount = self.kiwoom.dynamicCall("GetCommData(QString, QString, int, QString)", trcode, recordname, i, "보유수량")
            unit_price = self.kiwoom.dynamicCall("GetCommData(QString, QString, int, QString)", trcode, recordname, i, "매입가")

            self.item_slot[i] = item_code

            self.func_SET_TableData(1, i, 0, item_code, 0)
            self.func_SET_TableData(1, i, 1, item_name, 0)
            self.func_SET_TableData(1, i, 2, str(int(owncount)), 0)
            self.func_SET_TableData(1, i, 3, str(round(float(unit_price), 1)), 0)

            self.SetRealReg("0101", item_code, "10", 1)      ## 실시간 데이터 수신 등록
        
        print(self.now(), "[MAIN] [func_SET_Items] set items END")

    def load_etc_data(self) :
        ## deposit load
        self.func_GET_Deposit()
        QtTest.QTest.qWait(300)

        ## history load
        today = self.func_GET_Today()
        self.flag_HistoryData_Auto = 1
        self.func_GET_TradeHistory(today)
        QtTest.QTest.qWait(300)

        ## ordering load
        self.func_GET_Ordering(today)
        QtTest.QTest.qWait(300)

        ## daily profit load
        self.func_GET_DailyProfit(0)

    def func_stop_check(self):
        self.SetRealRemove("ALL", "ALL")
        timestamp = self.func_GET_CurrentTime()
        self.text_edit.append(timestamp + "Monitoring STOP")

        self.load_etc_data()
    def ORDER_BUY(self, item_code, qty, price, order_type) :
        print(self.now(), "[MAIN] [ORDER_BUY] : ", item_code, qty, price)
        slot = self.which_thread(item_code)[1]

        self.check_jumun[slot] = ['',0,0,0,0]      # init
        self.check_jumun[slot][0] = item_code
        self.check_jumun[slot][1] = qty
        self.check_jumun[slot][2] = price
        self.check_jumun[slot][3] = datetime.datetime.now().strftime('%H%M%S')
        self.check_jumun[slot][4] = order_type
        
        rqname = str(item_code) + str(slot) + "order_buy"
        screen_no = "0101"
        acc_no = ACCOUNT
        order_type = 1
        hogagb = "00"
        orgorderno = ""
        order = self.kiwoom.dynamicCall("SendOrder(QString, QString, QString, int, QString, int, int, QString, QString)",
                     [rqname, screen_no, acc_no, order_type, item_code, qty, price, hogagb, orgorderno])

        if order == 0 :
            self.func_check_jumun(item_code, slot)

    def func_check_jumun(self, item_code, item_slot) :
        slot = int(item_slot)
        # if self.check_jumun[slot][0] != 0 and self.check_jumun[slot][1] != 0 and self.check_jumun[slot][2] != 0 and self.check_jumun[slot][3] != 0 :
        rqname = str(item_code) + str(slot) + "check_jumun"
        self.kiwoom.dynamicCall("SetInputValue(QString, QString)", "계좌번호", ACCOUNT)
        self.kiwoom.dynamicCall("SetInputValue(QString, QString)", "전체종목구분", 0)
        self.kiwoom.dynamicCall("SetInputValue(QString, QString)", "매매구분", 0)
        self.kiwoom.dynamicCall("SetInputValue(QString, QString)", "종목코드", item_code)
        self.kiwoom.dynamicCall("SetInputValue(QString, QString)", "체결구분", 0)
        self.kiwoom.dynamicCall("CommRqData(QString, QString, int, QString)", rqname, "opt10075", 0, "0101")
    def res_check_jumun(self, rqname, trcode, recordname, item_code, item_slot) :
        slot = int(item_slot)

        qty = self.check_jumun[slot][1]
        price = self.check_jumun[slot][2]
        
        data_cnt = int(self.func_GET_RepeatCount(trcode, rqname))

        o_time = int(int(self.check_jumun[slot][3]) / 100)
        o_time_p1 = o_time + 1
        o_time_m1 = o_time - 1

        if (o_time_m1 % 100) == 99 :
            o_time_m1_f = int(o_time_m1 / 100)
            o_time_m1 = o_time_m1_f * 100 + 59

        if (o_time_p1 % 100) == 60 :
            o_time_p1_f = int(o_time_m1 / 100)
            o_time_p1 = (o_time_p1_f+1) * 100 + 59

        # print("o time : ", o_time, o_time_m1, o_time_p1)
        res = 0

        for i in range(data_cnt) :
            jumun_item_code = self.kiwoom.dynamicCall("GetCommData(QString, QString, int, QString)", trcode, recordname, i, "종목코드").strip()
            jumun_qty = self.kiwoom.dynamicCall("GetCommData(QString, QString, int, QString)", trcode, recordname, i, "주문수량").replace('+', '').replace('-', '').strip()
            jumun_price = self.kiwoom.dynamicCall("GetCommData(QString, QString, int, QString)", trcode, recordname, i, "주문가격").replace('+', '').replace('-', '').strip()
            jumun_time = self.kiwoom.dynamicCall("GetCommData(QString, QString, int, QString)", trcode, recordname, i, "시간").strip()

            jumun_time = int(int(jumun_time)/100)
            # print(i, " : ", jumun_item_code, jumun_qty, jumun_price, jumun_time)

            if item_code == jumun_item_code :
                # if int(jumun_qty) == int(self.check_jumun[slot][0]) and int(jumun_price) == int(self.check_jumun[slot][1]) :
                # if (int(jumun_qty) == int(self.check_jumun_2[1])) and (int(jumun_price) == int(self.check_jumun_2[2])) :
                if (int(jumun_qty) == int(qty)) and (int(jumun_price) == int(price)) :      ## 주문 수량과 주문 가격이 동일한 놈들 중
                    if jumun_time == o_time or jumun_time == o_time_p1 or jumun_time == o_time_m1 :         ## 주문 시간을 비교해서 같은 놈을 찾음
                        res = 1

        if res == 1 :                                                   ## 주문내역이 있는 경우
            print(self.now(), "[MAIN]", "res_check_jumun : ORDER RCV PROPERLY")
            ## do nothing

        elif res == 0 :                                                 ## 주문내역이 없는 경우
            if self.check_jumun_times == 3 :                            ## jumun receive 여부 3회까지 확인
                self.check_jumun_times = 0                              ## re init
                print(self.now(), "[MAIN]", "res_check_jumun : ORDER RCV NOT PROPERTY")

                if slot == 0 :
                    self.worker0.not_ordered(item_code)
                elif slot == 1 :
                    self.worker1.not_ordered(item_code)
                elif slot == 2 :
                    self.worker2.not_ordered(item_code)
                elif slot == 3 :
                    self.worker3.not_ordered(item_code)
                elif slot == 4 :
                    self.worker4.not_ordered(item_code)

                # che_dict = {}
                # che_dict['th_num'] = slot
                # che_dict['item_code'] = item_code
                # che_dict['res'] = 0
                # self.che_dict.emit(che_dict)

                if self.check_jumun[slot][3] == 9 :                     ## item find를 통해 buy 하는 경우
                    self.item_finder_req = 0
                    self.item_slot[slot] = 0                            ## slot 해제
                    self.reply_buy.emit(1)                              ## 주문이 안들어 갔으므로 item finder 재 기동
            
            else :
                self.check_jumun_times = self.check_jumun_times + 1
                QtTest.QTest.qWait(2000)                                 ## 500 ms delay
                self.func_check_jumun(item_code, slot)                  ## re-check jumun
        
    def ORDER_SELL(self, item_code, qty, price) :
        rqname = "RQ_TEST"
        screen_no = "0101"
        acc_no = ACCOUNT
        order_type = 2
        hogagb = "00"
        orgorderno = ""
        
        order = self.kiwoom.dynamicCall("SendOrder(QString, QString, QString, int, QString, int, int, QString, QString)",
                     [rqname, screen_no, acc_no, order_type, item_code, qty, price, hogagb, orgorderno])
        
        # self.func_UPDATE_db_item(item_code, 2, 1)       # oerdered -> 1
        print(self.now(), "[MAIN] [ORDER_SELL] : ", item_code, qty, price)
    ## 매수 ##
    def func_ORDER_BUY(self) :
        timestamp = self.func_GET_CurrentTime()
        self.text_edit.append(timestamp + "Clicked : BUY")
        try:
            item_code = self.code_edit.text()

            already = self.which_thread(item_code)[0]
            th_num = self.which_thread(item_code)[1]

            qty = int(self.buy_sell_count.text())
            price = int(self.wid_sell_price.text())

            print(self.now(), "[MAIN] [func_ORDER_BUY] : ", item_code, qty, price, th_num)

            test_dict = {}
            test_dict['autoTrade'] = 0
            test_dict['item_code'] = item_code

            if self.item_finder_req == 1 :          ## item finder의 요청에 의해 구매하는 경우
                test_dict['orderType'] = 9
            
            else :
                if already == 0 :                   ## 신규 item manual BUY
                    test_dict['orderType'] = 5
                elif already == 1 :                 ## 기존 item manual BUY
                    test_dict['orderType'] = 6

            test_dict['qty'] = qty
            test_dict['price'] = price
            test_dict['deposit'] = int(self.wid_show_deposit_d2.text())
            
            self.item_slot[th_num] = item_code

            if th_num == 0 :
                # print(now, "[MAIN]", "th_num : ", th_num)
                self.test_dict0.emit(test_dict)
            elif th_num == 1 :
                # print(now, "[MAIN]", "th_num : ", th_num)
                self.test_dict1.emit(test_dict)
            elif th_num == 2 :
                # print(now, "[MAIN]", "th_num : ", th_num)
                self.test_dict2.emit(test_dict)
            elif th_num == 3 :
                # print(now, "[MAIN]", "th_num : ", th_num)
                self.test_dict3.emit(test_dict)
            elif th_num == 4 :
                # print(now, "[MAIN]", "th_num : ", th_num)
                self.test_dict4.emit(test_dict)

        except Exception as e:
            timestamp = self.func_GET_CurrentTime()
            self.text_edit.append(timestamp + str(e))

            pass
    ## 매도 ##
    def func_ORDER_SELL(self) :
        try:
            item_code = self.code_edit.text()
            th_num = self.which_thread(item_code)[1]
            own_count = int(self.table_summary.item(th_num, 2).text())
            qty = int(self.buy_sell_count.text())
            price = self.wid_buy_price.text()
            print(self.now(), "[MAIN] [func_ORDER_SELL] : ", item_code, qty, price, th_num)

            test_dict = {}
            test_dict['autoTrade'] = 0
            test_dict['item_code'] = item_code
            test_dict['deposit'] = int(self.wid_show_deposit_d2.text())

            if qty > own_count :
                print(self.now(), "[MAIN] [func_ORDER_SELL] : SELL Qty Exceed")
                
            elif qty < own_count :
                test_dict['orderType'] = 7
                
            elif qty == own_count :
                test_dict['orderType'] = 8
                
            test_dict['qty'] = qty
            test_dict['price'] = price

            if th_num == 0 :
                # print(now, "[MAIN]", "send dict -> ", th_num)
                self.test_dict0.emit(test_dict)
            elif th_num == 1 :
                # print(now, "[MAIN]", "send dict -> ", th_num)
                self.test_dict1.emit(test_dict)
            elif th_num == 2 :
                # print(now, "[MAIN]", "send dict -> ", th_num)
                self.test_dict2.emit(test_dict)
            elif th_num == 3 :
                # print(now, "[MAIN]", "send dict -> ", th_num)
                self.test_dict3.emit(test_dict)
            elif th_num == 4 :
                # print(now, "[MAIN]", "send dict -> ", th_num)
                self.test_dict4.emit(test_dict)

        except Exception as e:
            timestamp = self.func_GET_CurrentTime()
            self.text_edit.append(timestamp + str(e))

    def func_restart_check(self, th_num, item_code) :
        rqname = "RESET_" + str(th_num) + '_' + item_code

        self.reset_time = self.reset_time + 1

        acc_no = ACCOUNT
        acc_pw = PASSWORD
        self.kiwoom.dynamicCall("SetInputValue(QString, QString)", "계좌번호", acc_no)
        self.kiwoom.dynamicCall("SetInputValue(QString, QString)", "비밀번호", acc_pw)
        self.kiwoom.dynamicCall("CommRqData(QString, QString, int, QString)", rqname, "opw00018", 0, self.reset_time)       # 잔고 출력

        # print(now, "[MAIN]", "[func_restart_check] ORDER COMPLETE")

    def func_RESET_Items(self, rqname, trcode, recordname, slot, code) :
        slot = int(slot)

        item_count = int(self.func_GET_RepeatCount(trcode, rqname))

        for i in range(item_count) :
            item_code = self.kiwoom.dynamicCall("GetCommData(QString, QString, int, QString)", trcode, recordname, i, "종목번호").replace('A', '').strip()
            if item_code == code :
                item_name = self.kiwoom.dynamicCall("GetCommData(QString, QString, int, QString)", trcode, recordname, i, "종목명").strip()
                owncount = self.kiwoom.dynamicCall("GetCommData(QString, QString, int, QString)", trcode, recordname, i, "보유수량")
                unit_price = self.kiwoom.dynamicCall("GetCommData(QString, QString, int, QString)", trcode, recordname, i, "매입가")
                break
        
        self.func_SET_TableData(1, slot, 0, item_code, 0)
        self.func_SET_TableData(1, slot, 1, item_name, 0)
        self.func_SET_TableData(1, slot, 2, str(int(owncount)), 0)
        self.func_SET_TableData(1, slot, 3, str(round(float(unit_price), 1)), 0)

        # print(now, "[MAIN]", "[func_RESET_Items] Complete")
        che_dict = {}
        che_dict['th_num'] = slot
        che_dict['item_code'] = item_code
        che_dict['res'] = 1

        self.che_dict.emit(che_dict)
        # self.reset_slot[slot] = 0               ## reset slot을 0으로 setting 하여 reset이 완료되었음을 확인

    def func_GET_Chejan_data(self, fid):
        ret = self.kiwoom.dynamicCall("GetChejanData(int)", fid)
        return ret
    def func_RECEIVE_Chejan_data(self, gubun, item_cnt, fid_list):
        order_id = item_code = item_name = trade_price = trade_amount = remained = trade_time = 'n'
        if gubun == "0" :       
            # receive_type = self.func_GET_Chejan_data(913)         # 주문상태(접수, 확인, 체결)
            # trade_type = self.func_GET_Chejan_data(907)           # 매도수구분(1: 매도, 2: 매수)
            order_id = self.func_GET_Chejan_data(9203)              # 주문번호
            item_code = self.func_GET_Chejan_data(9001)             # 종목코드
            item_name = self.func_GET_Chejan_data(302)              # 종목명
            trade_amount = self.func_GET_Chejan_data(911)           # 체결량
            remained = self.func_GET_Chejan_data(902)               # 미체결
            trade_time = self.func_GET_Chejan_data(908)             # 주문체결시간

            today = self.func_GET_Today()
            self.func_GET_Ordering(today)                           ## 주문상황을 실시간으로 반영

            # 데이터가 여러번 표시되는 것이 아니라 다 받은 후 일괄로 처리되기 위함
            if remained == '0':         # 체결시
                item_code = item_code.replace('A', '').strip()
                # print(now, "[MAIN]", "CHE RECEIVE : ", item_code)

                # if item_code == self.buying_item :              ## item find를 통해 구매한 내역일 경우 item finder에 finish signal send
                #     self.reply_buy.emit(1)

                timestamp = self.func_GET_CurrentTime()
                
                self.text_edit.append(timestamp + "[체결완료]" + "[" + trade_time+"]" + order_id + ':' + item_code + '/' + item_name.strip() + '/' + trade_amount + '(' + remained + ')')
                # print(self.now(), "[MAIN] [체결완료]" + "[" + trade_time+"]" + order_id + ':' + item_code + '/' + item_name.strip() + '/' + trade_amount + '(' + remained + ')')
                print(self.now(), "[MAIN] [체결완료] : ", order_id, item_code, trade_amount)

                orderType = self.func_GET_db_item(item_code, 3)
                if orderType != "none" :
                    if orderType == 1 :
                        th_num = self.which_thread(item_code)[1]
                        # print(now, "[MAIN]", "[CHEJAN] ADD Water / slot : ", th_num)

                        if self.DELETE_Table_Summary_item(th_num) == 0 :        ## table의 데이터를 다 지웠을 경우 0
                            self.func_restart_check(th_num, item_code)

                    elif orderType == 2 :
                        # print(now, "[MAIN]", "[CHEJAN] SELL & BUY(SELL)")
                        th_num = self.which_thread(item_code)[1]
                        # print(now, "[MAIN]", "[2] THREAD NUM : ", th_num)

                        if self.DELETE_Table_Summary_item(th_num) == 0 :
                            self.func_restart_check(th_num, item_code)

                    elif orderType == 3 :                                   ## Full Sell 일 경우
                        # print(now, "[MAIN]", "[CHEJAN] FULL SELL(Auto)")
                        th_num = self.which_thread(item_code)[1]
                        # print(now, "[MAIN]", "[3] THREAD NUM : ", th_num)
                        self.item_slot[th_num] = 0      ## unassign slot
                        # print(now, "[MAIN]", "[3] Slot unassign Complete")
                        
                        if self.DELETE_Table_Summary_item(th_num) == 0 :    ## table data 삭제
                            self.SetRealRemove("ALL", item_code)            ## 실시간 데이터 감시 해제

                            che_dict = {}
                            che_dict['th_num'] = th_num
                            che_dict['item_code'] = item_code
                            che_dict['res'] = 1
                            self.che_dict.emit(che_dict)                    ## 결과 전송

                    elif orderType == 4 :
                        # print(now, "[MAIN]", "[CHEJAN] SELL & BUY(BUY)")
                        th_num = self.which_thread(item_code)[1]
                        # print(now, "[MAIN]", "[4] THREAD NUM : ", th_num)

                        if self.DELETE_Table_Summary_item(th_num) == 0 :
                            self.func_restart_check(th_num, item_code)

                    elif orderType == 5 :                                   ## BUY NEW(manual)
                        # print(now, "[MAIN]", "[CHEJAN] BUY(MANUAL)")
                        th_num = self.which_thread(item_code)[1]
                        # print(now, "[MAIN]", "[5] THREAD NUM : ", th_num)

                        if self.DELETE_Table_Summary_item(th_num) == 0 :
                            self.func_restart_check(th_num, item_code)
                            self.SetRealReg("0101", item_code, "10", 1)      ## 실시간 데이터 수신 등록

                    elif orderType == 6 :       ## gi buy (manual)
                        # print(now, "[MAIN]", "[CHEJAN] GI BUY(MANUAL)")
                        th_num = self.which_thread(item_code)[1]
                        # print(now, "[MAIN]", "[6] THREAD NUM : ", th_num)

                        if self.DELETE_Table_Summary_item(th_num) == 0 :        ## table의 데이터를 다 지웠을 경우 0
                            self.func_restart_check(th_num, item_code)

                    elif orderType == 7 :       ## sell(manual)
                        # print(now, "[MAIN]", "[CHEJAN] SELL(MANUAL)")
                        th_num = self.which_thread(item_code)[1]
                        # print(now, "[MAIN]", "[7] THREAD NUM : ", th_num)
                        
                        if self.DELETE_Table_Summary_item(th_num) == 0 :        ## table의 데이터를 다 지웠을 경우 0
                            self.func_restart_check(th_num, item_code)

                    elif orderType == 8 :       ## manual Sell Full
                        # print(now, "[MAIN]", "[CHEJAN] FULL SELL(MANUAL)")
                        th_num = self.which_thread(item_code)[1]
                        # print(now, "[MAIN]", "[8] THREAD NUM : ", th_num)
                        self.item_slot[th_num] = 0      ## unassign slot
                        # print(now, "[MAIN]", "[8] Slot unassign Complete")

                        if self.DELETE_Table_Summary_item(th_num) == 0 :
                            self.SetRealRemove("ALL", item_code)        ## 실시간 데이터 감시 해제

                            che_dict = {}
                            che_dict['th_num'] = th_num
                            che_dict['item_code'] = item_code
                            che_dict['res'] = 1
                            self.che_dict.emit(che_dict)        ## 결과 
                    
                    elif orderType == 9 :       ## new buy by item finding
                        self.reply_buy.emit(1)
                        # print(now, "[MAIN]", "[CHEJAN] BUY(ITEM FINDER)")
                        th_num = self.which_thread(item_code)[1]
                        # print(now, "[MAIN]", "[9] THREAD NUM : ", th_num)

                        self.item_finder_req = 0

                        if self.DELETE_Table_Summary_item(th_num) == 0 :
                            self.func_restart_check(th_num, item_code)
                            self.SetRealReg("0101", item_code, "10", 1)      ## 실시간 데이터 수신 등록

                    self.load_etc_data()

            # today = self.func_GET_Today()
            # self.func_GET_Ordering(today)
                
    def func_GET_Deposit(self) :
        acc_no = ACCOUNT
        acc_pw = PASSWORD
        self.kiwoom.dynamicCall("SetInputValue(QString, QString)", "계좌번호", acc_no)
        self.kiwoom.dynamicCall("SetInputValue(QString, QString)", "비밀번호", acc_pw)
        self.kiwoom.dynamicCall("CommRqData(QString, QString, int, QString)", "GET_Deposit", "opw00001", 0, "0101")
    def func_SHOW_Deposit(self, rqname, trcode, recordname) :
        deposit = self.kiwoom.dynamicCall("GetCommData(QString, QString, int, QString)", trcode, recordname, 0, "예수금")
        d_1 = self.kiwoom.dynamicCall("GetCommData(QString, QString, int, QString)", trcode, recordname, 0, "d+1추정예수금")
        d_2 = self.kiwoom.dynamicCall("GetCommData(QString, QString, int, QString)", trcode, recordname, 0, "d+2추정예수금")
        # orderable_money = self.kiwoom.dynamicCall("GetCommData(QString, QString, int, QString)", trcode, recordname, 0, "주문가능금액")

        # str('{0:,}'.format())
        self.wid_show_deposit.setText(str('{0:,}'.format(int(deposit))))
        self.wid_show_deposit_d1.setText(str('{0:,}'.format(int(d_1))))
        self.wid_show_deposit_d2.setText(str(int(d_2)))
        # self.wid_show_orderable_money.setText(str('{0:,}'.format(int(orderable_money))))

        self.set_deposit = 1

    def func_GET_DailyProfit(self, input) :
        acc_no = ACCOUNT
        acc_pw = PASSWORD

        if input == 0:
            year = strftime("%Y", localtime())
            month = strftime("%m", localtime())

            start_day = year + month + "01"
            end_day = self.func_GET_Today()
        
        elif input == 1:
            start_day = self.input_ds_start.text()
            end_day = self.input_ds_end.text()

        self.kiwoom.dynamicCall("SetInputValue(QString, QString)", "계좌번호", acc_no)
        self.kiwoom.dynamicCall("SetInputValue(QString, QString)", "시작일자", start_day)
        self.kiwoom.dynamicCall("SetInputValue(QString, QString)", "종료일자", end_day)
        self.kiwoom.dynamicCall("CommRqData(QString, QString, int, QString)", "GET_DailyProfit", "opt10074", 0, "0101")

        self.show_ds_start.setText(start_day)
        self.show_ds_end.setText(end_day)
    def func_SHOW_DailyProfit(self, rqname, trcode, recordname):
        self.table_dailyprofit.clearContents()      ## table clear
        data_cnt = int(self.func_GET_RepeatCount(trcode, rqname))
        self.table_dailyprofit.setRowCount(0)
        self.table_dailyprofit.setRowCount(data_cnt)

        for i in range(data_cnt) :
            try :
                date = self.kiwoom.dynamicCall("GetCommData(QString, QString, int, QString)", trcode, recordname, i, "일자")
                total_buy = self.kiwoom.dynamicCall("GetCommData(QString, QString, int, QString)", trcode, recordname, i, "매수금액")
                total_sell = self.kiwoom.dynamicCall("GetCommData(QString, QString, int, QString)", trcode, recordname, i, "매도금액")
                profit = self.kiwoom.dynamicCall("GetCommData(QString, QString, int, QString)", trcode, recordname, i, "당일매도손익")
                fee = self.kiwoom.dynamicCall("GetCommData(QString, QString, int, QString)", trcode, recordname, i, "당일매매수수료")
                tax = self.kiwoom.dynamicCall("GetCommData(QString, QString, int, QString)", trcode, recordname, i, "당일매매세금")

                self.func_SET_TableData(4, i, 0, date.strip(), 0)
                self.func_SET_TableData(4, i, 1, total_buy.strip(), 0)
                self.func_SET_TableData(4, i, 2, total_sell.strip(), 0)

                if int(profit) == 0 :
                    self.func_SET_TableData(4, i, 3, profit.strip(), 0)
                elif int(profit) > 0 :
                    self.func_SET_TableData(4, i, 3, profit.strip(), 1)
                elif int(profit) < 0 :
                    self.func_SET_TableData(4, i, 3, profit.strip(), 2)
                self.func_SET_TableData(4, i, 4, fee.strip(), 0)
                self.func_SET_TableData(4, i, 5, tax.strip(), 0)

            except :
                pass

    def func_GET_TradeHistory(self, date) :       # search history data manually
        if self.flag_HistoryData_Auto == 1:
            self.search_date = date
            self.flag_HistoryData_Auto = 0
        else :
            self.search_date = self.input_history_date.text()

        acc_no = ACCOUNT
        acc_pw = PASSWORD
        self.kiwoom.dynamicCall("SetInputValue(QString, QString)", "주문일자", self.search_date)
        self.kiwoom.dynamicCall("SetInputValue(QString, QString)", "계좌번호", acc_no)
        self.kiwoom.dynamicCall("SetInputValue(QString, QString)", "비밀번호", acc_pw)
        self.kiwoom.dynamicCall("SetInputValue(QString, QString)", "비밀번호입력매체구분", "00")
        self.kiwoom.dynamicCall("SetInputValue(QString, QString)", "주식채권구분", "0")
        self.kiwoom.dynamicCall("CommRqData(QString, QString, int, QString)", "GET_History", "opw00009", 0, self.reset_time)
    def func_SHOW_TradeHistory(self, rqname, trcode, recordname):
        data_cnt = self.kiwoom.dynamicCall("GetCommData(QString, QString, int, QString)", trcode, recordname, 0, "조회건수")

        if data_cnt == "":
            self.table_history.clearContents()
            self.table_history.setRowCount(1)
            self.table_history.setSpan(0,0,1,9)
            self.func_SET_TableData(2, 0, 0, "체결내역 없음", 0)
        else :
            data_cnt = int(data_cnt)
            self.table_history.clearContents()
            self.table_history.setRowCount(0)
            self.table_history.setRowCount(data_cnt)

            self.df_history = self.df_history.drop(self.df_history.index[:len(self.df_history)])        ## df_history 초기화

            for i in range(data_cnt) :
                try:
                    deal_type = self.kiwoom.dynamicCall("GetCommData(QString, QString, int, QString)", trcode, recordname, i, "주문유형구분")
                    trade_no = self.kiwoom.dynamicCall("GetCommData(QString, QString, int, QString)", trcode, recordname, i, "체결번호")
                    trade_time = self.kiwoom.dynamicCall("GetCommData(QString, QString, int, QString)", trcode, recordname, i, "체결시간")
                    itemcode = self.kiwoom.dynamicCall("GetCommData(QString, QString, int, QString)", trcode, recordname, i, "종목번호")
                    item_name = self.kiwoom.dynamicCall("GetCommData(QString, QString, int, QString)", trcode, recordname, i, "종목명")
                    trade_amount = self.kiwoom.dynamicCall("GetCommData(QString, QString, int, QString)", trcode, recordname, i, "체결수량")
                    trade_unit_price = self.kiwoom.dynamicCall("GetCommData(QString, QString, int, QString)", trcode, recordname, i, "체결단가")
                    req_no = self.kiwoom.dynamicCall("GetCommData(QString, QString, int, QString)", trcode, recordname, i, "주문번호")

                    # self.df_history.loc[i] = [self.search_date, trade_time, deal_type, trade_no, itemcode, item_name, int(trade_amount), round(float(trade_unit_price), 1), req_no]
                    self.df_history.loc[i] = [trade_time, deal_type, trade_no, itemcode, item_name, int(trade_amount), int(trade_unit_price), req_no]
                except:
                    pass

            self.df_history = self.df_history.sort_values(by=['time'], axis=0, ascending=False)
            self.df_history = self.df_history.reset_index(drop=True, inplace=False)

            data_cnt = len(self.df_history)

            for i in range(data_cnt):
                try:
                    # self.func_SET_TableData(2, i, 0, self.df_history.day[i], 0)
                    self.func_SET_TableData(2, i, 0, self.df_history.time[i], 0)
                    self.func_SET_TableData(2, i, 1, self.df_history.type[i], 0)
                    self.func_SET_TableData(2, i, 2, self.df_history.T_ID[i], 0)
                    self.func_SET_TableData(2, i, 3, self.df_history.Code[i].replace('A', '').strip(), 0)
                    self.func_SET_TableData(2, i, 4, self.df_history.Name[i].strip(), 0)
                    self.func_SET_TableData(2, i, 5, str(self.df_history.Qty[i]), 0)
                    self.func_SET_TableData(2, i, 6, str(self.df_history.Price[i]), 0)
                    self.func_SET_TableData(2, i, 7, str(self.df_history.Req_ID[i]), 0)
                except:
                    pass

        try:
            self.wid_history_day.setText(self.search_date)
        except:
            pass

    def func_GET_Ordering(self, today):
        acc_no = ACCOUNT
        acc_pw = PASSWORD

        self.kiwoom.dynamicCall("SetInputValue(QString, QString)", "주문일자", today)
        self.kiwoom.dynamicCall("SetInputValue(QString, QString)", "계좌번호", acc_no)
        self.kiwoom.dynamicCall("SetInputValue(QString, QString)", "비밀번호", acc_pw)
        self.kiwoom.dynamicCall("SetInputValue(QString, QString)", "비밀번호입력매체구분", "00")
        self.kiwoom.dynamicCall("SetInputValue(QString, QString)", "조회구분", '1')
        self.kiwoom.dynamicCall("SetInputValue(QString, QString)", "주식채권구분", 0)
        self.kiwoom.dynamicCall("CommRqData(QString, QString, int, QString)", "GET_Ordering", "OPW00007", 0, "0101")
    def func_SHOW_Ordering(self, rqname, trcode, recordname) :
        data_cnt = int(self.func_GET_RepeatCount(trcode, rqname))

        if data_cnt == 0:
            self.table_order.clearContents()
            self.table_order.setRowCount(1)
            self.table_order.setSpan(0,0,1,8)
            self.func_SET_TableData(3, 0, 0, "미체결내역 없음", 0)

        else :
            self.table_order.clearContents()
            self.table_order.setRowCount(0)
            self.table_order.setRowCount(data_cnt)

            self.df_ordering = self.df_ordering.drop(self.df_ordering.index[:len(self.df_ordering)])        ## df_ordering 초기화

            for i in range(data_cnt):
                
                try:
                    order_id = self.kiwoom.dynamicCall("GetCommData(QString, QString, int, QString)", trcode, recordname, i, "주문번호")
                    item_code = self.kiwoom.dynamicCall("GetCommData(QString, QString, int, QString)", trcode, recordname, i, "종목번호")
                    item_name = self.kiwoom.dynamicCall("GetCommData(QString, QString, int, QString)", trcode, recordname, i, "종목명")
                    deal_type = self.kiwoom.dynamicCall("GetCommData(QString, QString, int, QString)", trcode, recordname, i, "주문구분")
                    order_time = self.kiwoom.dynamicCall("GetCommData(QString, QString, int, QString)", trcode, recordname, i, "주문시간")
                    order_amount = self.kiwoom.dynamicCall("GetCommData(QString, QString, int, QString)", trcode, recordname, i, "주문수량")
                    trade_amount = self.kiwoom.dynamicCall("GetCommData(QString, QString, int, QString)", trcode, recordname, i, "체결수량")
                    remained = self.kiwoom.dynamicCall("GetCommData(QString, QString, int, QString)", trcode, recordname, i, "주문잔량")

                    self.df_ordering.loc[i] = [deal_type.strip(), order_id, order_time, item_code.replace('A', '').strip(), item_name.strip(), str(int(order_amount)), str(int(trade_amount)), int(remained)]

                except:
                    pass

            self.df_ordering = self.df_ordering.sort_values(by=['remained', 'order_time'], axis=0, ascending=[False, False])
            self.df_ordering = self.df_ordering.reset_index(drop=True, inplace=False)

            for i in range(len(self.df_ordering)):
                try:
                    self.func_SET_TableData(3, i, 0, self.df_ordering.deal_type[i], 0)
                    self.func_SET_TableData(3, i, 1, self.df_ordering.order_id[i], 0)
                    self.func_SET_TableData(3, i, 2, self.df_ordering.order_time[i], 0)
                    self.func_SET_TableData(3, i, 3, self.df_ordering.item_code[i], 0)
                    self.func_SET_TableData(3, i, 4, self.df_ordering.item_name[i], 0)
                    self.func_SET_TableData(3, i, 5, self.df_ordering.order_amount[i], 0)
                    self.func_SET_TableData(3, i, 6, self.df_ordering.trade_amount[i], 0)
                    if self.df_ordering.remained[i] > 0 :
                        self.func_SET_TableData(3, i, 7, str(self.df_ordering.remained[i]), 1)
                    elif self.df_ordering.remained[i] == 0 :
                        self.func_SET_TableData(3, i, 7, str(self.df_ordering.remained[i]), 0)
                except:
                    pass

    def func_GET_ItemInfo(self, code):
        try :
            item_code = self.code_edit.text()
            self.GET_hoga(item_code)
        except :
            pass
    def func_GET_ItemInfo_by_click(self, index) :
        row = index.row()
        try:
            item_code = self.table_summary.item(row, 0).text()
            item_code = item_code.replace("A", "")
            # self.flag_ItemInfo_click = 1
            self.code_edit.setText(item_code.strip())

            hoga_buy = self.table_summary.item(row, 5).text()
            hoga_sell = self.table_summary.item(row, 6).text()
            self.wid_buy_price.setText(str(int(hoga_buy)))
            self.wid_sell_price.setText(str(int(hoga_sell)))

            self.kiwoom.dynamicCall("SetInputValue(QString, QString)", "종목코드", item_code)
            self.kiwoom.dynamicCall("CommRqData(QString, QString, int, QString)", "GET_ItemInfo", "opt10001", 0, "0101")
        except:
            pass
    def func_SHOW_ItemInfo(self, rqname, trcode, recordname):
        item_code = self.kiwoom.dynamicCall("GetCommData(QString, QString, int, QString)", trcode, recordname, 0, "종목코드")
        name = self.kiwoom.dynamicCall("GetCommData(QString, QString, int, QString)", trcode, recordname, 0, "종목명")
        volume = self.kiwoom.dynamicCall("GetCommData(QString, QString, int, QString)", trcode, recordname, 0, "거래량")
        numStocks = self.kiwoom.dynamicCall("GetCommData(QString, QString, int, QString)", trcode, recordname, 0, "상장주식")
        prices = self.kiwoom.dynamicCall("GetCommData(QString, QString, int, QString)", trcode, recordname, 0, "시가")
        percent = self.kiwoom.dynamicCall("GetCommData(QString, QString, int, QString)", trcode, recordname, 0, "등락율")
        per = self.kiwoom.dynamicCall("GetCommData(QString, QString, int, QString)", trcode, recordname, 0, "PER")
        current_price = self.kiwoom.dynamicCall("GetCommData(QString, QString, int, QString)", trcode, recordname, 0, "현재가")
        current_price = self.kiwoom.dynamicCall("GetCommData(QString, QString, int, QString)", trcode, recordname, 0, "현재가").replace('+', '').replace('-', '').strip()

        self.te_iteminfo_code.setText(item_code.strip())
        self.te_iteminfo_name.setText(name.strip())
        self.te_iteminfo_price.setText(current_price)
        self.te_iteminfo_vol.setText(volume.strip())
        self.te_iteminfo_percent.setText(percent.strip() + " %")

    def GET_hoga(self, item_code):
        # hoga 창에 호가 입력
        self.kiwoom.dynamicCall("SetInputValue(QString, QString)", "종목코드", item_code)
        self.kiwoom.dynamicCall("CommRqData(QString, QString, int, QString)", "SET_hoga", "opt10004", 0, "0101")

        # item information 호출
        self.kiwoom.dynamicCall("SetInputValue(QString, QString)", "종목코드", item_code)
        self.kiwoom.dynamicCall("CommRqData(QString, QString, int, QString)", "GET_ItemInfo", "opt10001", 0, "0101")
    def SET_hoga(self, rqname, trcode, recordname) :
        hoga_buy = self.kiwoom.dynamicCall("GetCommData(QString, QString, int, QString)", trcode, recordname, 0, "매수최우선호가").replace('+', '').replace('-', '')
        hoga_sell = self.kiwoom.dynamicCall("GetCommData(QString, QString, int, QString)", trcode, recordname, 0, "매도최우선호가").replace('+', '').replace('-', '')

        self.wid_buy_price.setText(hoga_buy)
        self.wid_sell_price.setText(hoga_sell)

    def func_GET_CurrentTime(self) :
        year = strftime("%Y", localtime())
        month = strftime("%m", localtime())
        day = strftime("%d", localtime())
        hour = strftime("%H", localtime())
        cmin = strftime("%M", localtime())
        sec = strftime("%S", localtime())

        now = "[" + year + "/" + month +"/" + day + " " + hour + ":" + cmin + ":" + sec + "] "

        return now
    def func_GET_CurrentTime2(self) :
        month = strftime("%m", localtime())
        day = strftime("%d", localtime())
        hour = strftime("%H", localtime())
        cmin = strftime("%M", localtime())
        sec = strftime("%S", localtime())

        now = month +"/" + day + " " + hour + ":" + cmin + ":" + sec

        return now
    def func_GET_RepeatCount(self, trcode, rqname):
        ret = self.kiwoom.dynamicCall("GetRepeatCnt(QString, QString)", trcode, rqname)
        return ret
    def func_GET_Today(self):
        year = strftime("%Y", localtime())
        month = strftime("%m", localtime())
        day = strftime("%d", localtime())
        today = year + month + day

        return today
    
    @pyqtSlot(int)
    def check_slot(self, data) :
        self.res_check_slot.emit(self.item_slot)
    @pyqtSlot(int)
    def refresh_status(self, data) :
        ref_time = self.func_GET_CurrentTime2()
        self.load_etc_data()
        self.wid_refresh_order.setText(ref_time)
    @pyqtSlot(dict)
    def auto_buy(self, data) :
        item_code = data['item_code']
        qty = data['qty']
        price = data['price']
        print(self.now(), "[MAIN] [auto buy] : ", item_code, qty, price)

        self.code_edit.setText(item_code)
        self.buy_sell_count.setText(str(qty))
        self.wid_buy_price.setText(str(price))
        self.wid_sell_price.setText(str(price))
        self.buying_item = item_code
        self.item_finder_req = 1

        self.func_ORDER_BUY()

    def event_connect(self, err_code):
        if err_code == 0:
            timestamp = self.func_GET_CurrentTime()
            self.text_edit.append(timestamp + "Login Complete")

            self.timer = module_timer.Timer()
            self.timer.cur_time.connect(self.update_times)
            self.timer.check_slot.connect(self.check_slot)
            self.timer.req_buy.connect(self.auto_buy)
            self.timer.refresh_status.connect(self.refresh_status)
            self.res_check_slot.connect(self.timer.res_check_slot)
            self.reply_buy.connect(self.timer.reply_buy)
            self.timer.start()

            timestamp = self.func_GET_CurrentTime()
            self.text_edit.append(timestamp + "Timer Thread Started")
            self.func_GET_Deposit()

            while True :
                if self.set_deposit == 1:
                    self.set_deposit = 0
                    break
                QtTest.QTest.qWait(100)

            self.func_start_check()          # Aloha
            
        else:
            print(self.now(), "[MAIN] Login Failed")
            try :
                self.kiwoom.dynamicCall("CommConnect()")        ## aloha
            except :
                pass
    
    def func_SET_tableSUMMARY(self):
        row_count = 5
        col_count = SUMMARY_COL_CNT
        self.table_summary.setRowCount(row_count)
        self.table_summary.setColumnCount(col_count)
        self.table_summary.resizeRowsToContents()

        for i in range(col_count):
            self.table_summary.setColumnWidth(i, 100)
        
        self.table_summary.setColumnWidth(0, 75)
        self.table_summary.setColumnWidth(2, 65)
        self.table_summary.setColumnWidth(12, 65)
        self.table_summary.setColumnWidth(13, 65)
        self.table_summary.setColumnWidth(14, 65)
        self.table_summary.setColumnWidth(15, 65)

        
        self.table_summary.verticalHeader().setVisible(False)
        self.table_summary.verticalHeader().setDefaultSectionSize(1)
        
        self.table_summary.setHorizontalHeaderItem(0, QTableWidgetItem("코드"))
        self.table_summary.setHorizontalHeaderItem(1, QTableWidgetItem("종목"))
        self.table_summary.setHorizontalHeaderItem(2, QTableWidgetItem("수량"))
        self.table_summary.setHorizontalHeaderItem(3, QTableWidgetItem("단가"))
        self.table_summary.setHorizontalHeaderItem(4, QTableWidgetItem("현재가"))
        self.table_summary.setHorizontalHeaderItem(5, QTableWidgetItem("매도최"))
        self.table_summary.setHorizontalHeaderItem(6, QTableWidgetItem("매수최"))
        self.table_summary.setHorizontalHeaderItem(7, QTableWidgetItem("매입금액"))
        self.table_summary.setHorizontalHeaderItem(8, QTableWidgetItem("평가금액"))
        self.table_summary.setHorizontalHeaderItem(9, QTableWidgetItem("합계"))
        self.table_summary.setHorizontalHeaderItem(10, QTableWidgetItem("수수료"))
        self.table_summary.setHorizontalHeaderItem(11, QTableWidgetItem("손익"))
        self.table_summary.setHorizontalHeaderItem(12, QTableWidgetItem("%"))
        self.table_summary.setHorizontalHeaderItem(13, QTableWidgetItem("단계"))
        self.table_summary.setHorizontalHeaderItem(14, QTableWidgetItem("HIGH"))
        self.table_summary.setHorizontalHeaderItem(15, QTableWidgetItem("체강"))
        

        self.table_summary.clicked.connect(self.func_GET_ItemInfo_by_click)
    def func_SET_tableHISTORY(self):
        row_count = 0
        col_count = 8
        # self.table_history.resize(722, 250)
        
        self.table_history.setRowCount(row_count)
        self.table_history.setColumnCount(col_count)
        self.table_history.resizeRowsToContents()
        # self.table_history.resizeColumnsToContents()

        for i in range(col_count):
            self.table_history.setColumnWidth(i, 100)

        self.table_history.verticalHeader().setVisible(False)
        self.table_history.verticalHeader().setDefaultSectionSize(1)
        self.table_history.setHorizontalHeaderItem(0, QTableWidgetItem("체결시간"))
        self.table_history.setHorizontalHeaderItem(1, QTableWidgetItem("구분"))
        self.table_history.setHorizontalHeaderItem(2, QTableWidgetItem("체결번호"))
        self.table_history.setHorizontalHeaderItem(3, QTableWidgetItem("종목번호"))
        self.table_history.setHorizontalHeaderItem(4, QTableWidgetItem("종 목 명"))
        self.table_history.setHorizontalHeaderItem(5, QTableWidgetItem("체결수량"))
        self.table_history.setHorizontalHeaderItem(6, QTableWidgetItem("체결단가"))
        self.table_history.setHorizontalHeaderItem(7, QTableWidgetItem("주문번호"))
    def func_SET_tableORDER(self):
        row_count = 0
        col_count = 8

        self.table_order.setRowCount(row_count)
        self.table_order.setColumnCount(col_count)
        self.table_order.resizeRowsToContents()

        for i in range(col_count):
            self.table_order.setColumnWidth(i, 100)

        self.table_order.verticalHeader().setVisible(False)
        self.table_order.verticalHeader().setDefaultSectionSize(1)
        self.table_order.setHorizontalHeaderItem(0, QTableWidgetItem("구분"))
        self.table_order.setHorizontalHeaderItem(1, QTableWidgetItem("주문번호"))
        self.table_order.setHorizontalHeaderItem(2, QTableWidgetItem("주문시간"))
        self.table_order.setHorizontalHeaderItem(3, QTableWidgetItem("종목번호"))
        self.table_order.setHorizontalHeaderItem(4, QTableWidgetItem("종목명"))
        self.table_order.setHorizontalHeaderItem(5, QTableWidgetItem("주문량"))
        self.table_order.setHorizontalHeaderItem(6, QTableWidgetItem("체결량"))
        self.table_order.setHorizontalHeaderItem(7, QTableWidgetItem("미체결"))
    def func_SET_table_dailyprofit(self):
        row_count = 0
        col_count = 6

        self.table_dailyprofit.setRowCount(row_count)
        self.table_dailyprofit.setColumnCount(col_count)
        self.table_dailyprofit.resizeRowsToContents()

        for i in range(col_count):
            self.table_dailyprofit.setColumnWidth(i, 100)

        self.table_dailyprofit.verticalHeader().setVisible(False)
        self.table_dailyprofit.verticalHeader().setDefaultSectionSize(1)
        self.table_dailyprofit.setHorizontalHeaderItem(0, QTableWidgetItem("일자"))
        self.table_dailyprofit.setHorizontalHeaderItem(1, QTableWidgetItem("매수금액"))
        self.table_dailyprofit.setHorizontalHeaderItem(2, QTableWidgetItem("매도금액"))
        self.table_dailyprofit.setHorizontalHeaderItem(3, QTableWidgetItem("매도손익"))
        self.table_dailyprofit.setHorizontalHeaderItem(4, QTableWidgetItem("수수료"))
        self.table_dailyprofit.setHorizontalHeaderItem(5, QTableWidgetItem("세금"))
    def func_SET_TableData(self, table_no, row, col, content, color):
        item = QTableWidgetItem(content)
        item.setTextAlignment(4)    # 가운데 정렬
        if color == 1:
            item.setForeground(QBrush(Qt.red)) # 글자색
        elif color == 2:
            item.setForeground(QBrush(Qt.blue)) # 글자색

        # summary table
        if table_no == 1:
            self.table_summary.setItem(row, col, item)
        # history table
        if table_no == 2:
            self.table_history.setItem(row, col, item)
        # order table
        if table_no == 3:
            self.table_order.setItem(row, col, item)
        if table_no == 4:
            self.table_dailyprofit.setItem(row, col, item)

    def SetRealReg(self, screenNo, item_code, fid, realtype):
        self.kiwoom.dynamicCall("SetRealReg(QString, QString, QString, QString)", screenNo, item_code, fid, realtype)
    def SetRealRemove(self, screenNo, item_code):
        self.kiwoom.dynamicCall("SetRealRemove(QString, QString)", screenNo, item_code)

    def receive_tr_data(self, screen_no, rqname, trcode, recordname, prev_next, data_len, err_code, msg1, msg2):
        print(self.now(), "[MAIN] [receive_tr_data] : ", rqname)
        reset_str = "RESET_"

        if "order_buy" in rqname :
            item_code = rqname[0:6]
            item_slot = rqname[6:7]
            self.func_check_jumun(item_code, item_slot)

        if reset_str in rqname:
            item_slot = int(rqname[6:7])
            item_code = rqname[8:]
            self.func_RESET_Items(rqname, trcode, recordname, item_slot, item_code)
        
        if "jan_check" in rqname :
            item_code = rqname[0:6]
            item_slot = rqname[6:7]
            self.result_get_hoga(rqname, trcode, recordname, item_code, item_slot)

        if "check_jumun" in rqname :
            item_code = rqname[0:6]
            item_slot = rqname[6:7]
            self.res_check_jumun(rqname, trcode, recordname, item_code, item_slot)
        
        if rqname == "SET_hoga":
            self.SET_hoga(rqname, trcode, recordname)
        if rqname == "GET_DailyProfit":
            self.func_SHOW_DailyProfit(rqname, trcode, recordname)
        if rqname == "SETTING":
            self.func_SET_Items(rqname, trcode, recordname)
        if rqname == "GET_Deposit":
            self.func_SHOW_Deposit(rqname, trcode, recordname)
        if rqname == "GET_ItemInfo":
            self.func_SHOW_ItemInfo(rqname, trcode, recordname)
        if rqname == "GET_Ordering":
            self.func_SHOW_Ordering(rqname, trcode, recordname)
        if rqname == "opw00018_req":
            self.func_SHOW_CheckBalance(rqname, trcode, recordname)
        if rqname == "GET_History":
            self.func_SHOW_TradeHistory(rqname, trcode, recordname)
    def receive_real_data(self, code, real_type, real_data): 
        # print(now, "[MAIN]", "receive real : ", code)
        # print("[MAIN] receive real : ", code)
        if self.possible_time == 1 and self.send_data == 1 :
            th_num = self.which_thread(code)[1]
            cur_price = self.kiwoom.dynamicCall("GetCommRealData(QString, int)", code, 10).replace('+', '').replace('-', '').strip()
            # jan = self.kiwoom.dynamicCall("GetCommRealData(QString, int)", code, 61).replace('+', '').replace('-', '').strip()
            if cur_price != '' :
                try :
                    price_sell = self.kiwoom.dynamicCall("GetCommRealData(QString, int)", code, 27).replace('+', '').replace('-', '').strip()       ## 매도 최우선가
                    price_buy = self.kiwoom.dynamicCall("GetCommRealData(QString, int)", code, 28).replace('+', '').replace('-', '').strip()        ## 매수 최우선가

                    chegang = self.kiwoom.dynamicCall("GetCommRealData(QString, int)", code, 228)
                    
                    item_name = self.table_summary.item(th_num, 1).text()
                    own_count = self.table_summary.item(th_num, 2).text()
                    unit_price = self.table_summary.item(th_num, 3).text()

                    test_dict = {}
                    
                    test_dict['item_code'] = code
                    test_dict['item_name'] = item_name
                    test_dict['own_count'] = int(own_count)
                    test_dict['unit_price'] = float(unit_price)
                    test_dict['cur_price'] = int(cur_price)
                    test_dict['price_buy'] = int(price_buy)
                    test_dict['price_sell'] = int(price_sell)
                    test_dict['chegang'] = float(chegang)
                    test_dict['deposit'] = int(self.wid_show_deposit_d2.text())

                    test_dict['autoTrade'] = 1

                    if th_num == 0 :
                        self.test_dict0.emit(test_dict)
                    elif th_num == 1 :
                        self.test_dict1.emit(test_dict)
                    elif th_num == 2 :
                        self.test_dict2.emit(test_dict)
                    elif th_num == 3 :
                        self.test_dict3.emit(test_dict)
                    elif th_num == 4 :
                        self.test_dict4.emit(test_dict)
                
                except :
                    pass
        
        else :
            timestamp = self.func_GET_CurrentTime()
            self.text_edit.append(timestamp + "Market NOT OPEN")

    def func_SET_db_table(self) :
        conn = sqlite3.connect("item_status.db")
        cur = conn.cursor()
        sql = "create table if not exists STATUS (code text, step integer, ordered integer, orderType integer, trAmount integer)"
        cur.execute(sql)
        conn.commit()
        conn.close()
    def func_GET_db_item(self, code, col):
        conn = sqlite3.connect("item_status.db")
        cur = conn.cursor()
        if col == 0:        # get all codes
            sql = "select code from STATUS"
            cur.execute(sql)
            rows = cur.fetchall()
            conn.close()

            if rows is None :
                return "none"
            else:
                codes = []
                for row in rows:
                    codes.append(row[0])
                return codes
        else :
            if col == 1:        # get step
                sql = "select step from STATUS where code = ?"
                cur.execute(sql, [code])
            elif col == 2:      # get ordered
                sql = "select ordered from STATUS where code = ?"
                cur.execute(sql, [code])
            elif col == 3:      # get orderType
                sql = "select orderType from STATUS where code = ?"
                cur.execute(sql, [code])
            elif col == 4:      # get trAmount
                sql = "select trAmount from STATUS where code = ?"
                cur.execute(sql, [code])

            row = cur.fetchone()
            conn.close()

            if row is None:
                return "none"
            else:
                return row[0]
    def func_INSERT_db_item(self, code, step, ordered, orderType, trAmount):
        conn = sqlite3.connect("item_status.db")
        cur = conn.cursor()
        sql = "insert into STATUS (code, step, ordered, orderType, trAmount) values(:CODE, :STEP, :ORDERED, :ORDERTYPE, :TRAMOUNT)"
        cur.execute(sql, {"CODE" : code, "STEP" : step, "ORDERED" : ordered, "ORDERTYPE" : orderType, "TRAMOUNT" : trAmount})
        conn.commit()
        conn.close()
        print(self.now(), "[MAIN] [func_INSERT_db_item] : INSERTED")
    # def func_UPDATE_db_item(self, code, col, data) :
    #     conn = sqlite3.connect("item_status.db")
    #     cur = conn.cursor()
    #     if col == 1:    # update step
    #         sql = "update STATUS set step = :DATA where code = :CODE"    
    #         cur.execute(sql, {"DATA" : data, "CODE" : code})
    #     elif col == 2:  # update ordered
    #         sql = "update STATUS set ordered = :DATA where code = :CODE"    
    #         cur.execute(sql, {"DATA" : data, "CODE" : code})
    #     elif col == 3:  # update orderType
    #         sql = "update STATUS set orderType = :DATA where code = :CODE"    
    #         cur.execute(sql, {"DATA" : data, "CODE" : code})
    #         #### type ####
    #         # 0 : normai(default)
    #         # 1 : 물타기
    #         # 2 : 수익실현 및 복구
    #         # 3 : full 매도
    #         # 4 : 존버
    #     elif col == 4:  # update trAmount
    #         sql = "update STATUS set trAmount = :DATA where code = :CODE"    
    #         cur.execute(sql, {"DATA" : data, "CODE" : code})

    #     conn.commit()
    #     conn.close()
    #     success = cur.rowcount
    #     # print(now, "[MAIN]", "UPDATED")
    #     return success
    def func_DELETE_db_item(self, code):
        conn = sqlite3.connect("item_status.db")
        cur = conn.cursor()
        sql = "delete from STATUS where code = :CODE"
        cur.execute(sql, {"CODE" : code})
        conn.commit()
        conn.close()
        print(self.now(), "[MAIN] [func_DELETE_db_item] : DELETED")

    def which_thread(self, item_code) :
        th_num = [0, 100]

        ## 기존에 할당되어 있는지 우선 검색
        for i in range(NUM_SLOT) :
            if item_code == self.item_slot[i] :
                th_num[0] = 1
                th_num[1] = i
                break
        
        ## 기존에 할당이 안되어 있을 경우 가장 먼저 비어있는 slot 할당
        if th_num[1] == 100 :
            for i in range(NUM_SLOT) :
                if self.item_slot[i] == 0 :
                    th_num[0] = 0
                    th_num[1] = i
                    break
        
        return th_num

if __name__=="__main__":
    app = QApplication(sys.argv)
    app.setStyle(QStyleFactory.create('Fusion')) # --> 없으면, 헤더색 변경 안됨.
    # print(now, "[MAIN]", sys.argv)
    myWindow = Kiwoom()
    myWindow.show()
    app.exec_()
    