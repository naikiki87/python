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
import target

form_class = uic.loadUiType("interface.ui")[0]

# TARGET_ITEMS = target.ITEMS

ACCOUNT = config.ACCOUNT
PASSWORD = config.PASSWORD
NUM_SLOT = config.NUM_SLOT
SUMMARY_TITLES = ["code", "item", "qty", "unit_p", "매입(A)", "p_BUY", "평가(B)", "수수료(C)", "손익(B-A-C)", "%", "step", "vol_ratio", "vol_sell", "vol_buy"]
SUMMARY_COL_CNT = len(SUMMARY_TITLES)
RP_TITLES = ["code", "item", "qty", "unit_p", "t_purchase", "price_buy", "t_evaluation", "total_fee", "total_sum", "percent", "step", "vol_ratio", "vol_sell", "vol_buy"]

# print("TARGET : ", len(TARGET_ITEMS))

class Kiwoom(QMainWindow, form_class):
    # real_dict = pyqtSignal(dict)
    test_dict0 = pyqtSignal(dict)
    test_dict1 = pyqtSignal(dict)
    test_dict2 = pyqtSignal(dict)
    test_dict3 = pyqtSignal(dict)
    test_dict4 = pyqtSignal(dict)
    test_dict5 = pyqtSignal(dict)
    test_dict6 = pyqtSignal(dict)
    test_dict7 = pyqtSignal(dict)
    test_dict8 = pyqtSignal(dict)
    test_dict9 = pyqtSignal(dict)
    test_dict10 = pyqtSignal(dict)
    test_dict11 = pyqtSignal(dict)
    test_dict12 = pyqtSignal(dict)
    test_dict13 = pyqtSignal(dict)
    test_dict14 = pyqtSignal(dict)

    che_dict = pyqtSignal(dict)
    res_check_slot = pyqtSignal(list)
    reply_buy = pyqtSignal(int)
    reply_first_check = pyqtSignal(dict)
    sig_timer_paused = pyqtSignal(int)
    sig_worker_resume = pyqtSignal(int)

    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.init_ENV()

        self.kiwoom = QAxWidget()
        self.kiwoom.setControl("KHOPENAPI.KHOpenAPICtrl.1")
        self.kiwoom.dynamicCall("CommConnect()")        ## aloha
        self.kiwoom.OnEventConnect.connect(self.event_connect)
        self.kiwoom.OnReceiveTrData.connect(self.receive_tr_data)
        self.kiwoom.OnReceiveRealData.connect(self.receive_real_data)
        self.kiwoom.OnReceiveChejanData.connect(self.func_RECEIVE_Chejan_data)


    def init_ENV(self) :
        self.pagenum = 2020
        ## flag setting

        self.tempi = 0
        self.win_check_deposit = 1000
        self.today = self.func_GET_Today()
        self.item_finder_req = 0
        
        # self.check_jumun_times = 0
        self.check_jan = []
        self.check_jumun = []
        self.first_check_jumun = []
        self.paused = []
        self.check_jumun_times = []
        self.first_check_times = []
        self.item_slot = []
        self.reset_slot = []
        self.list_th_connected = []
        for i in range(NUM_SLOT) :
            self.check_jan.append([0,0,0,0])
            self.check_jumun.append(['',0,0,0,0])
            self.first_check_jumun.append([''])
            self.paused.append(0)
            self.check_jumun_times.append(0)
            self.first_check_times.append(0)
            self.item_slot.append(0)
            self.reset_slot.append(0)
            self.list_th_connected.append(0)
            
        self.send_data = 1
        self.buying_item = 0
        # self.input_show_status.setText("STOP")

        self.possible_time = 0
        self.timezone = 0

        self.reset_time = 1000
        self.set_deposit = 0
        self.cnt_thread = 0
        
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
        # self.btn_START.clicked.connect(self.order_start)
        # self.btn_STOP.clicked.connect(self.order_stop)
        # self.btn_HISTORY.clicked.connect(self.func_GET_TradeHistory)
        # self.btn_dailyprofit.clicked.connect(lambda: self.func_GET_DailyProfit(1))

        ## table setting
        self.func_SET_tableSUMMARY()        # monitoring table
        # self.func_SET_tableHISTORY()        # history table
        self.func_SET_tableORDER()          # order 현황 table
        self.func_SET_table_dailyprofit()   # dailyprofit table

    def receive_real_data(self, code, real_type, real_data): 
        # print("[MAIN] receive real : ", code)
        if self.possible_time == 1 :
            slot = self.which_slot(code)
            if slot != -1 :
                try :
                    item_name = self.table_summary.item(slot, 1).text()
                    own_count = self.table_summary.item(slot, 2).text()
                    unit_price = self.table_summary.item(slot, 3).text()
                    
                    price_sell = int(self.kiwoom.dynamicCall("GetCommRealData(QString, int)", code, 41).replace('+', '').replace('-', '').strip())       ## 매도호가 수량 1
                    price_buy = int(self.kiwoom.dynamicCall("GetCommRealData(QString, int)", code, 51).replace('+', '').replace('-', '').strip())       ## 매도호가 수량 1
                    volume_sell = int(self.kiwoom.dynamicCall("GetCommRealData(QString, int)", code, 61).replace('+', '').replace('-', '').strip())       ## 매도호가 수량 1
                    volume_buy = int(self.kiwoom.dynamicCall("GetCommRealData(QString, int)", code, 71).replace('+', '').replace('-', '').strip())       ## 매도호가 수량 1
                    volume_ratio = round((volume_sell / volume_buy), 2)

                    temp = {}

                    temp['autoTrade'] = 1
                    temp['item_code'] = code
                    temp['item_name'] = item_name
                    temp['own_count'] = int(own_count)
                    temp['unit_price'] = float(unit_price)
                    temp['price_buy'] = price_buy
                    temp['price_sell'] = price_sell
                    # temp['deposit'] = int(self.wid_show_deposit_d2.text())
                    temp['volume_sell'] = volume_sell
                    temp['volume_buy'] = volume_buy
                    temp['volume_ratio'] = volume_ratio
                    temp['timezone'] = self.timezone
            
                    if slot == 0:
                        self.test_dict0.emit(temp)
                    elif slot == 1:
                        self.test_dict1.emit(temp)
                    elif slot == 2:
                        self.test_dict2.emit(temp)
                    elif slot == 3:
                        self.test_dict3.emit(temp)
                    elif slot == 4:
                        self.test_dict4.emit(temp)
                    elif slot == 5 :
                        self.test_dict5.emit(temp)
                    elif slot == 6 :
                        self.test_dict6.emit(temp)
                    elif slot == 7 :
                        self.test_dict7.emit(temp)
                    elif slot == 8 :
                        self.test_dict8.emit(temp)
                    elif slot == 9 :
                        self.test_dict9.emit(temp)
                    
                    elif slot == 10 :
                        self.test_dict10.emit(temp)
                    elif slot == 11 :
                        self.test_dict11.emit(temp)
                    elif slot == 12 :
                        self.test_dict12.emit(temp)
                    elif slot == 13 :
                        self.test_dict13.emit(temp)
                    elif slot == 14 :
                        self.test_dict14.emit(temp)

                except :
                    pass
            
        # else :
        #     print("Market Not Open")

    def get_now(self) :
        year = strftime("%Y", localtime())
        month = strftime("%m", localtime())
        day = strftime("%d", localtime())
        hour = strftime("%H", localtime())
        cmin = strftime("%M", localtime())
        sec = strftime("%S", localtime())

        now = "[" + year + "/" + month +"/" + day + " " + hour + ":" + cmin + ":" + sec + "] "

        return now

    @pyqtSlot(dict)
    def update_times(self, data) :
        self.text_edit4.setText(data['time'])
        self.possible_time = data['possible']
        self.timezone = data['timezone']

    @pyqtSlot(dict)
    def rp_dict(self, data):
        ordered = data['ordered']
        try :
            if ordered == 1 :                       ## indicate ordered
                self.table_summary.item(data['seq'], 0).setBackground(QtGui.QColor(0,255,0))
            elif ordered == 2 :                     ## indicate released
                self.table_summary.item(data['seq'], 0).setBackground(QtGui.QColor(255,255,255))
            elif ordered == 3 :                     ## indicate paused
                self.table_summary.item(data['seq'], 0).setBackground(QtGui.QColor(255,255,0))
            elif ordered == 4 :                     ## indicate paused2  
                self.table_summary.item(data['seq'], 0).setBackground(QtGui.QColor(247,129,129))
            elif ordered == 0 :                     ## indicate normal state
                self.table_summary.item(data['seq'], 0).setBackground(QtGui.QColor(255,255,255))

                for i in range(4, len(RP_TITLES), 1) :
                    if RP_TITLES[i] == "percent" :
                        if data[RP_TITLES[i]] > 0 :
                            self.func_SET_TableData(1, data['seq'], i, str(data[RP_TITLES[i]]), 1)
                        elif data[RP_TITLES[i]] < 0 :
                            self.func_SET_TableData(1, data['seq'], i, str(data[RP_TITLES[i]]), 2)
                        elif data[RP_TITLES[i]] == 0 :
                            self.func_SET_TableData(1, data['seq'], i, str(data[RP_TITLES[i]]), 0)
                    elif RP_TITLES[i] == "price_buy" :
                        self.func_SET_TableData(1, data['seq'], i, str(data[RP_TITLES[i]]), 1)    
                    else :
                        self.func_SET_TableData(1, data['seq'], i, str(data[RP_TITLES[i]]), 0)
            
        except :
            pass

    def show_pause(self, slot):
        try :
            self.table_summary.item(int(slot), 0).setBackground(QtGui.QColor(255,255,0))
        except :
            pass

    @pyqtSlot(int)
    def th_connected(self, data) :
        self.list_th_connected[self.th_seq] = data
        if 0 not in self.list_th_connected :
            print("2. ALL THREAD CONNECTED")

    def btn_test(self) :
        print("btn test")
        item_code = self.code_edit.text()

        res = self.kiwoom.dynamicCall("GetMasterStockState(QString)", item_code)
        print("res : ", res)
        print(type(res))
        
        # item_code = self.code_edit.text()
        # self.SetRealReg("0101", item_code, "10;41", "1")      ## 실시간 데이터 수신 등록

    def btn_test_2(self):
        self.SetRealRemove("ALL", "ALL")        ## 실시간 데이터 감시 해제


    def func_SHOW_ItemInfo_test(self, rqname, trcode, recordname):
        print("func show iteminfo test")
        item_code = self.kiwoom.dynamicCall("GetCommData(QString, QString, int, QString)", trcode, recordname, 0, "종목코드")
        name = self.kiwoom.dynamicCall("GetCommData(QString, QString, int, QString)", trcode, recordname, 0, "종목명")
        volume = self.kiwoom.dynamicCall("GetCommData(QString, QString, int, QString)", trcode, recordname, 0, "거래량")
        percent = self.kiwoom.dynamicCall("GetCommData(QString, QString, int, QString)", trcode, recordname, 0, "등락율")
        current_price = self.kiwoom.dynamicCall("GetCommData(QString, QString, int, QString)", trcode, recordname, 0, "현재가")
        current_price = self.kiwoom.dynamicCall("GetCommData(QString, QString, int, QString)", trcode, recordname, 0, "현재가").replace('+', '').replace('-', '').strip()

        print("name : ", name, volume, percent)
    
    def SET_hoga2(self, rqname, trcode, recordname) :
        print("SET hoga 2")
        # hoga_buy = self.kiwoom.dynamicCall("GetCommData(QString, QString, int, QString)", trcode, recordname, 0, "매수최우선호가").replace('+', '').replace('-', '')
        hoga_sell = self.kiwoom.dynamicCall("GetCommData(QString, QString, int, QString)", trcode, recordname, 0, "매도최우선호가").replace('+', '').replace('-', '')
        sell_0_vol = self.kiwoom.dynamicCall("GetCommData(QString, QString, int, QString)", trcode, recordname, 0, "매도최우선잔량").replace('+', '').replace('-', '')

        db_1_1 = self.kiwoom.dynamicCall("GetCommData(QString, QString, int, QString)", trcode, recordname, 0, "매도1차선잔량대비").replace('+', '').replace('-', '')

        hoga_sell_2 = self.kiwoom.dynamicCall("GetCommData(QString, QString, int, QString)", trcode, recordname, 0, "매도2차선호가").replace('+', '').replace('-', '')
        sell_2_vol = self.kiwoom.dynamicCall("GetCommData(QString, QString, int, QString)", trcode, recordname, 0, "매도2차선잔량").replace('+', '').replace('-', '')

        print("sell_0_vol : ", sell_0_vol, type(sell_0_vol))
        print("매도1차선잔량대비 : ", db_1_1)
        print("매도2차선호가 : ", hoga_sell_2)
        print("매도2차선잔량 : ", sell_2_vol)
        # print("hoga sell : ", hoga_sell)

    def check_deposit_2(self, rqname, trcode, recordname, item_slot, item_code) :
        slot = int(item_slot)

        # d1 = self.kiwoom.dynamicCall("GetCommData(QString, QString, int, QString)", trcode, recordname, 0, "d+1추정예수금")
        # d2 = self.kiwoom.dynamicCall("GetCommData(QString, QString, int, QString)", trcode, recordname, 0, "d+2추정예수금")
        # orderable_money = self.kiwoom.dynamicCall("GetCommData(QString, QString, int, QString)", trcode, recordname, 0, "주문가능금액")

        d1 = self.kiwoom.dynamicCall("GetCommData(QString, QString, int, QString)", trcode, recordname, 0, "예수금D+1")
        d2 = self.kiwoom.dynamicCall("GetCommData(QString, QString, int, QString)", trcode, recordname, 0, "예수금D+2")
        # orderable_money = self.kiwoom.dynamicCall("GetCommData(QString, QString, int, QString)", trcode, recordname, 0, "주문가능현금")

        qty = self.check_jan[slot][1]
        price = self.check_jan[slot][2]

        if (int(price) * int(qty)) <= int(d2) :
        # if (int(price) * int(qty)) <= int(orderable_money) :
            self.ORDER_BUY(item_code, self.check_jan[slot][1], self.check_jan[slot][2], self.check_jan[slot][3])
        
        else :
            if self.check_jan[slot][3] == 9 :                     ## item find를 통해 buy 하는 경우
                # if self.func_DELETE_db_item(item_code) == 1 :
                self.sig_worker_resume.emit(slot)
                self.item_finder_req = 0                            ## item finder req 해제
                self.item_slot[slot] = 0                            ## slot 해제
                self.reply_buy.emit(1)                              ## 주문이 안들어 갔으므로 item finder 재 기동
            
            else :
                if self.set_pause(int(slot)) == 1 :
                    self.table_summary.item(int(slot), 0).setBackground(QtGui.QColor(255,255,0))
                    self.sig_timer_paused.emit(slot)

        

    @pyqtSlot(dict)
    def rq_order(self, data) :
        buy_or_sell = data['type']
        item_code = data['item_code']
        qty = data['qty']
        price = data['price']

        if buy_or_sell == 0 :  ## BUY
            slot = self.which_thread(item_code)[1]
            order_type = data['order_type']

            self.check_jan[slot] = [0, 0, 0, 0]
            self.check_jan[slot][0] = item_code
            self.check_jan[slot][1] = qty
            self.check_jan[slot][2] = price
            self.check_jan[slot][3] = order_type

            if self.check_jan[slot][0] != 0 and self.check_jan[slot][1] != 0 and self.check_jan[slot][2] != 0 and self.check_jan[slot][3] != 0:
                self.tempi = self.tempi + 1
                rqname = str(item_code) + str(slot) + "check_deposit"
                self.win_check_deposit = self.win_check_deposit + 1

                # self.kiwoom.dynamicCall("SetInputValue(QString, QString)", "계좌번호", ACCOUNT)
                # self.kiwoom.dynamicCall("SetInputValue(QString, QString)", "비밀번호", PASSWORD)
                # self.kiwoom.dynamicCall("CommRqData(QString, QString, int, QString)", rqname, "opw00001", 0, str(self.win_check_deposit))


                self.kiwoom.dynamicCall("SetInputValue(QString, QString)", "계좌번호", ACCOUNT)
                self.kiwoom.dynamicCall("SetInputValue(QString, QString)", "비밀번호", PASSWORD)
                self.kiwoom.dynamicCall("CommRqData(QString, QString, int, QString)", rqname, "opw00005", 0, str(self.win_check_deposit))
        
        elif buy_or_sell == 1 :  ## SELL
            self.ORDER_SELL(item_code, qty, price)
    
    def pause_worker(self, slot, item_code) :
        if slot == 0 :
            self.worker0.pause_worker(item_code)
        elif slot == 1 :
            self.worker1.pause_worker(item_code)
        elif slot == 2 :
            self.worker2.pause_worker(item_code)
        elif slot == 3 :
            self.worker3.pause_worker(item_code)
        elif slot == 4 :
            self.worker4.pause_worker(item_code)

    def result_get_hoga(self, rqname, trcode, recordname, item_code, item_slot) :
        slot = int(item_slot)
        if item_code == self.check_jan[slot][0] :
            jan_sell = self.kiwoom.dynamicCall("GetCommData(QString, QString, int, QString)", trcode, recordname, 0, "매도최우선잔량").replace('+', '').replace('-', '').strip()
            if int(self.check_jan[slot][1]) <= int(jan_sell) :
                print(self.now(), "[MAIN] [result_get_hoga] Jan ENOUGH : ", jan_sell)
                self.ORDER_BUY(item_code, self.check_jan[slot][1], self.check_jan[slot][2], self.check_jan[slot][3])
            else :
                print(self.now(), "[MAIN] [result_get_hoga] Jan NOT ENOUGH : ", jan_sell)

                self.pause_worker(slot, item_code)

                if self.check_jan[slot][3] == 9 :       ## item find를 통해 신규 find인 경우
                    self.item_slot[slot] = 0            ## slot 해제
                    self.item_finder_req = 0
                    self.reply_buy.emit(1)                  # item finder 재 기동
        
    

    def DELETE_Table_Summary_item(self, slot) :
        try :
            for i in range(SUMMARY_COL_CNT) :
                self.func_SET_TableData(1, slot, i, "", 0)

            return 0

        except :
            self.DELETE_Table_Summary_item(slot)        ## recursive call
    
    def create_thread(self) :
        ## 1st        
        self.th_seq = 0
        self.worker0 = module_worker.Worker(0)
        self.worker0.th_con.connect(self.th_connected)
        self.test_dict0.connect(self.worker0.dict_from_main)
        self.che_dict.connect(self.worker0.che_result)
        self.reply_first_check.connect(self.worker0.reply_first_check)
        self.sig_worker_resume.connect(self.worker0.resume_paused)
        self.worker0.trans_dict.connect(self.rp_dict)
        self.worker0.rq_order.connect(self.rq_order)
        self.worker0.first_jumun_check.connect(self.first_rcv_jumun_check)
        self.worker0.start()
        while True :
            if self.list_th_connected[self.th_seq] == 1:
                break
            QtTest.QTest.qWait(100)
        ## 2nd
        self.th_seq = 1
        self.worker1 = module_worker.Worker(1)
        self.worker1.th_con.connect(self.th_connected)
        self.test_dict1.connect(self.worker1.dict_from_main)
        self.che_dict.connect(self.worker1.che_result)
        self.reply_first_check.connect(self.worker1.reply_first_check)
        self.sig_worker_resume.connect(self.worker1.resume_paused)
        self.worker1.trans_dict.connect(self.rp_dict)
        self.worker1.rq_order.connect(self.rq_order)
        self.worker1.first_jumun_check.connect(self.first_rcv_jumun_check)
        self.worker1.start()
        while True :
            if self.list_th_connected[self.th_seq] == 1:
                break
            QtTest.QTest.qWait(100)
        ## 3rd
        self.th_seq = 2
        self.worker2 = module_worker.Worker(2)
        self.worker2.th_con.connect(self.th_connected)
        self.test_dict2.connect(self.worker2.dict_from_main)
        self.che_dict.connect(self.worker2.che_result)
        self.reply_first_check.connect(self.worker2.reply_first_check)
        self.sig_worker_resume.connect(self.worker2.resume_paused)
        self.worker2.trans_dict.connect(self.rp_dict)
        self.worker2.rq_order.connect(self.rq_order)
        self.worker2.first_jumun_check.connect(self.first_rcv_jumun_check)
        self.worker2.start()
        while True :
            if self.list_th_connected[self.th_seq] == 1:
                break
            QtTest.QTest.qWait(100)
        ## 4th
        self.th_seq = 3
        self.worker3 = module_worker.Worker(3)
        self.worker3.th_con.connect(self.th_connected)
        self.test_dict3.connect(self.worker3.dict_from_main)
        self.che_dict.connect(self.worker3.che_result)
        self.reply_first_check.connect(self.worker3.reply_first_check)
        self.sig_worker_resume.connect(self.worker3.resume_paused)
        self.worker3.trans_dict.connect(self.rp_dict)
        self.worker3.rq_order.connect(self.rq_order)
        self.worker3.first_jumun_check.connect(self.first_rcv_jumun_check)
        self.worker3.start()
        while True :
            if self.list_th_connected[self.th_seq] == 1:
                break
            QtTest.QTest.qWait(100)

        ## 5th
        self.th_seq = 4
        self.worker4 = module_worker.Worker(4)
        self.worker4.th_con.connect(self.th_connected)
        self.test_dict4.connect(self.worker4.dict_from_main)
        self.che_dict.connect(self.worker4.che_result)
        self.reply_first_check.connect(self.worker4.reply_first_check)
        self.sig_worker_resume.connect(self.worker4.resume_paused)
        self.worker4.trans_dict.connect(self.rp_dict)
        self.worker4.rq_order.connect(self.rq_order)
        self.worker4.first_jumun_check.connect(self.first_rcv_jumun_check)
        self.worker4.start()
        while True :
            if self.list_th_connected[self.th_seq] == 1:
                break
            QtTest.QTest.qWait(100)

        ## 6th
        self.th_seq = 5
        self.worker5 = module_worker.Worker(self.th_seq)
        self.worker5.th_con.connect(self.th_connected)
        self.test_dict5.connect(self.worker5.dict_from_main)
        self.che_dict.connect(self.worker5.che_result)
        self.reply_first_check.connect(self.worker5.reply_first_check)
        self.sig_worker_resume.connect(self.worker5.resume_paused)
        self.worker5.trans_dict.connect(self.rp_dict)
        self.worker5.rq_order.connect(self.rq_order)
        self.worker5.first_jumun_check.connect(self.first_rcv_jumun_check)
        self.worker5.start()
        while True :
            if self.list_th_connected[self.th_seq] == 1:
                break
            QtTest.QTest.qWait(100)

        ## 7th
        self.th_seq = 6
        self.worker6 = module_worker.Worker(self.th_seq)
        self.worker6.th_con.connect(self.th_connected)
        self.test_dict6.connect(self.worker6.dict_from_main)
        self.che_dict.connect(self.worker6.che_result)
        self.reply_first_check.connect(self.worker6.reply_first_check)
        self.sig_worker_resume.connect(self.worker6.resume_paused)
        self.worker6.trans_dict.connect(self.rp_dict)
        self.worker6.rq_order.connect(self.rq_order)
        self.worker6.first_jumun_check.connect(self.first_rcv_jumun_check)
        self.worker6.start()
        while True :
            if self.list_th_connected[self.th_seq] == 1:
                break
            QtTest.QTest.qWait(100)

        ## 8th
        self.th_seq = 7
        self.worker7 = module_worker.Worker(self.th_seq)
        self.worker7.th_con.connect(self.th_connected)
        self.test_dict7.connect(self.worker7.dict_from_main)
        self.che_dict.connect(self.worker7.che_result)
        self.reply_first_check.connect(self.worker7.reply_first_check)
        self.sig_worker_resume.connect(self.worker7.resume_paused)
        self.worker7.trans_dict.connect(self.rp_dict)
        self.worker7.rq_order.connect(self.rq_order)
        self.worker7.first_jumun_check.connect(self.first_rcv_jumun_check)
        self.worker7.start()
        while True :
            if self.list_th_connected[self.th_seq] == 1:
                break
            QtTest.QTest.qWait(100)

        ## 9th
        self.th_seq = 8
        self.worker8 = module_worker.Worker(self.th_seq)
        self.worker8.th_con.connect(self.th_connected)
        self.test_dict8.connect(self.worker8.dict_from_main)
        self.che_dict.connect(self.worker8.che_result)
        self.reply_first_check.connect(self.worker8.reply_first_check)
        self.sig_worker_resume.connect(self.worker8.resume_paused)
        self.worker8.trans_dict.connect(self.rp_dict)
        self.worker8.rq_order.connect(self.rq_order)
        self.worker8.first_jumun_check.connect(self.first_rcv_jumun_check)
        self.worker8.start()
        while True :
            if self.list_th_connected[self.th_seq] == 1:
                break
            QtTest.QTest.qWait(100)

        ## 10th
        self.th_seq = 9
        self.worker9 = module_worker.Worker(self.th_seq)
        self.worker9.th_con.connect(self.th_connected)
        self.test_dict9.connect(self.worker9.dict_from_main)
        self.che_dict.connect(self.worker9.che_result)
        self.reply_first_check.connect(self.worker9.reply_first_check)
        self.sig_worker_resume.connect(self.worker9.resume_paused)
        self.worker9.trans_dict.connect(self.rp_dict)
        self.worker9.rq_order.connect(self.rq_order)
        self.worker9.first_jumun_check.connect(self.first_rcv_jumun_check)
        self.worker9.start()
        while True :
            if self.list_th_connected[self.th_seq] == 1:
                break
            QtTest.QTest.qWait(100)

        ## 11th
        self.th_seq = 10
        self.worker10 = module_worker.Worker(self.th_seq)
        self.worker10.th_con.connect(self.th_connected)
        self.test_dict10.connect(self.worker10.dict_from_main)
        self.che_dict.connect(self.worker10.che_result)
        self.reply_first_check.connect(self.worker10.reply_first_check)
        self.sig_worker_resume.connect(self.worker10.resume_paused)
        self.worker10.trans_dict.connect(self.rp_dict)
        self.worker10.rq_order.connect(self.rq_order)
        self.worker10.first_jumun_check.connect(self.first_rcv_jumun_check)
        self.worker10.start()
        while True :
            if self.list_th_connected[self.th_seq] == 1:
                break
            QtTest.QTest.qWait(100)

        ## 12th
        self.th_seq = 11
        self.worker11 = module_worker.Worker(self.th_seq)
        self.worker11.th_con.connect(self.th_connected)
        self.test_dict11.connect(self.worker11.dict_from_main)
        self.che_dict.connect(self.worker11.che_result)
        self.reply_first_check.connect(self.worker11.reply_first_check)
        self.sig_worker_resume.connect(self.worker11.resume_paused)
        self.worker11.trans_dict.connect(self.rp_dict)
        self.worker11.rq_order.connect(self.rq_order)
        self.worker11.first_jumun_check.connect(self.first_rcv_jumun_check)
        self.worker11.start()
        while True :
            if self.list_th_connected[self.th_seq] == 1:
                break
            QtTest.QTest.qWait(100)

        ## 13th
        self.th_seq = 12
        self.worker12 = module_worker.Worker(self.th_seq)
        self.worker12.th_con.connect(self.th_connected)
        self.test_dict12.connect(self.worker12.dict_from_main)
        self.che_dict.connect(self.worker12.che_result)
        self.reply_first_check.connect(self.worker12.reply_first_check)
        self.sig_worker_resume.connect(self.worker12.resume_paused)
        self.worker12.trans_dict.connect(self.rp_dict)
        self.worker12.rq_order.connect(self.rq_order)
        self.worker12.first_jumun_check.connect(self.first_rcv_jumun_check)
        self.worker12.start()
        while True :
            if self.list_th_connected[self.th_seq] == 1:
                break
            QtTest.QTest.qWait(100)

        ## 14th
        self.th_seq = 13
        self.worker13 = module_worker.Worker(self.th_seq)
        self.worker13.th_con.connect(self.th_connected)
        self.test_dict13.connect(self.worker13.dict_from_main)
        self.che_dict.connect(self.worker13.che_result)
        self.reply_first_check.connect(self.worker13.reply_first_check)
        self.sig_worker_resume.connect(self.worker13.resume_paused)
        self.worker13.trans_dict.connect(self.rp_dict)
        self.worker13.rq_order.connect(self.rq_order)
        self.worker13.first_jumun_check.connect(self.first_rcv_jumun_check)
        self.worker13.start()
        while True :
            if self.list_th_connected[self.th_seq] == 1:
                break
            QtTest.QTest.qWait(100)

        ## 15th
        self.th_seq = 14
        self.worker14 = module_worker.Worker(self.th_seq)
        self.worker14.th_con.connect(self.th_connected)
        self.test_dict14.connect(self.worker14.dict_from_main)
        self.che_dict.connect(self.worker14.che_result)
        self.reply_first_check.connect(self.worker14.reply_first_check)
        self.sig_worker_resume.connect(self.worker14.resume_paused)
        self.worker14.trans_dict.connect(self.rp_dict)
        self.worker14.rq_order.connect(self.rq_order)
        self.worker14.first_jumun_check.connect(self.first_rcv_jumun_check)
        self.worker14.start()
        while True :
            if self.list_th_connected[self.th_seq] == 1:
                break
            QtTest.QTest.qWait(100)
        
        return 0

    @pyqtSlot(dict)
    def first_rcv_jumun_check(self, data) :
        print("first rcv jumun check : ", data)
        slot = data['slot']
        item_code = data['item_code']
        self.first_check_jumun[slot] = item_code

        self.first_rcv_jumun_check_2(slot, item_code)

    def first_rcv_jumun_check_2(self, item_slot, item_code) :
        rqname = str(item_code) + str(item_slot) + "first_jumun_check"
        self.kiwoom.dynamicCall("SetInputValue(QString, QString)", "계좌번호", ACCOUNT)
        self.kiwoom.dynamicCall("SetInputValue(QString, QString)", "전체종목구분", 0)
        self.kiwoom.dynamicCall("SetInputValue(QString, QString)", "매매구분", 0)
        self.kiwoom.dynamicCall("SetInputValue(QString, QString)", "종목코드", item_code)
        self.kiwoom.dynamicCall("SetInputValue(QString, QString)", "체결구분", 0)
        if self.kiwoom.dynamicCall("CommRqData(QString, QString, int, QString)", rqname, "opt10075", 0, "0102") != 0 :
            self.first_rcv_jumun_check_2(item_slot, item_code)

    def res_first_check_jumun(self, rqname, trcode, recordname, item_code, item_slot) :
        # print("res check jumun status : ", item_slot, item_code)
        res = 0
        slot = int(item_slot)
        data_cnt = int(self.func_GET_RepeatCount(trcode, rqname))

        for i in range(data_cnt) :
            jumun_item_code = self.kiwoom.dynamicCall("GetCommData(QString, QString, int, QString)", trcode, recordname, i, "종목코드").strip()
            jumun_qty = self.kiwoom.dynamicCall("GetCommData(QString, QString, int, QString)", trcode, recordname, i, "주문수량").replace('+', '').replace('-', '').strip()
            jumun_price = self.kiwoom.dynamicCall("GetCommData(QString, QString, int, QString)", trcode, recordname, i, "주문가격").replace('+', '').replace('-', '').strip()
            jumun_time = self.kiwoom.dynamicCall("GetCommData(QString, QString, int, QString)", trcode, recordname, i, "시간").strip()
            jumun_mi = int(self.kiwoom.dynamicCall("GetCommData(QString, QString, int, QString)", trcode, recordname, i, "미체결수량").replace('+', '').replace('-', '').strip())

            # print(i, jumun_item_code, jumun_qty, jumun_price, jumun_time, jumun_mi)
            if item_code == jumun_item_code :
                if jumun_mi > 0 :
                    res = 1
        if res == 0 :                                                 ## 주문내역이 없는 경우
            if self.first_check_times[slot] == 2 :                            ## jumun receive 여부 3회까지 확인
                self.first_check_times[slot] = 0                              ## re init
                print("[FIRST CHECK] : ", slot, item_code, " : NO")
                # self.table_summary.item(int(slot), 0).setBackground(QtGui.QColor(255,255,255))

                temp = {}
                temp['slot'] = slot
                temp['item_code'] = item_code
                self.reply_first_check.emit(temp)

            else :
                self.first_check_times[slot] = self.first_check_times[slot] + 1
                QtTest.QTest.qWait(500)                                 ## 100 ms delay
                self.first_rcv_jumun_check_2(slot, item_code)           ## recheck
        
        elif res == 1 :                     ## 첫 확인시 주문 내역이 있는 경우
            self.first_check_times[slot] = 0


    def order_start(self) :
        try :
            self.send_data = 1
            # self.input_show_status.setText("RUNNING")
        except Exception as e : 
            print(e)
        self.load_etc_data()
    def order_stop(self) :
        try :
            self.send_data = 0
            # self.input_show_status.setText("STOP")
        except Exception as e : 
            print(e)
        self.load_etc_data()
    def func_start_check(self) :
        self.load_etc_data()
        if self.create_thread() == 0 :              ## thread creation
            self.table_summary.clearContents()      ## table clear
            self.kiwoom.dynamicCall("SetInputValue(QString, QString)", "계좌번호", ACCOUNT)
            self.kiwoom.dynamicCall("SetInputValue(QString, QString)", "비밀번호", PASSWORD)
            self.kiwoom.dynamicCall("CommRqData(QString, QString, int, QString)", "SETTING", "opw00018", 0, "0101")         ## 계좌 잔고 조회
    def func_SET_Items(self, rqname, trcode, recordname):
        self.item_count = int(self.func_GET_RepeatCount(trcode, rqname))
        db_codes = self.func_GET_db_item(0, 0)

        for i in range(self.item_count) :
            try :
                item_code = self.kiwoom.dynamicCall("GetCommData(QString, QString, int, QString)", trcode, recordname, i, "종목번호").replace('A', '').strip()
                db_codes.remove(item_code)
            except :
                pass

        for i in range(len(db_codes)) :
            self.func_DELETE_db_item(db_codes[i])

        for i in range(self.item_count) :
            try :
                item_code = self.kiwoom.dynamicCall("GetCommData(QString, QString, int, QString)", trcode, recordname, i, "종목번호").replace('A', '').strip()
                step = self.func_GET_db_item(item_code, 1)

                if step == "none" :
                    self.func_INSERT_db_item(item_code, 0, 0, 0, -1.5)
            except :
                pass

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

            self.SetRealReg("0101", item_code, "41", "1")      ## 실시간 데이터 수신 등록
        
        print("3. ITEM SETTING FINISHED")
        print("-- READY --")

    def load_etc_data(self) :
        ## deposit load
        self.func_GET_Deposit()
        QtTest.QTest.qWait(300)

        ## history load
        self.flag_HistoryData_Auto = 1
        # self.func_GET_TradeHistory(self.today)
        # QtTest.QTest.qWait(300)

        ## ordering load
        self.func_GET_Ordering(self.today)
        QtTest.QTest.qWait(300)

        ## daily profit load
        self.func_GET_DailyProfit(0)

    def func_stop_check(self):
        self.SetRealRemove("ALL", "ALL")
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
        order = self.kiwoom.dynamicCall("SendOrder(QString, QString, QString, int, QString, int, int, QString, QString)",
                    #  [rqname, "0101", ACCOUNT, 1, item_code, qty, price, "00", ""])         ## 지정가 매수
                     [rqname, "0101", ACCOUNT, 1, item_code, qty, 0, "03", ""])         ## 시장가 매수
                    #  [rqname, screen_no, ACCOUNT, order_type, item_code, qty, price, hogagb, orgorderno])

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

        # print("Order : ", item_code, qty, price, o_time)

        for i in range(data_cnt) :
            jumun_item_code = self.kiwoom.dynamicCall("GetCommData(QString, QString, int, QString)", trcode, recordname, i, "종목코드").strip()
            jumun_qty = self.kiwoom.dynamicCall("GetCommData(QString, QString, int, QString)", trcode, recordname, i, "주문수량").replace('+', '').replace('-', '').strip()
            jumun_price = self.kiwoom.dynamicCall("GetCommData(QString, QString, int, QString)", trcode, recordname, i, "주문가격").replace('+', '').replace('-', '').strip()
            jumun_time = self.kiwoom.dynamicCall("GetCommData(QString, QString, int, QString)", trcode, recordname, i, "시간").strip()
            jumun_time = int(int(jumun_time)/100)

            # print(i, jumun_item_code, jumun_qty, jumun_price, jumun_time)

            if item_code == jumun_item_code :
                # if (int(jumun_qty) == int(qty)) and (int(jumun_price) == int(price)) :      ## 주문 수량과 주문 가격이 동일한 놈들 중
                if int(jumun_qty) == int(qty) :      ## 주문 수량과 주문 가격이 동일한 놈들 중
                    if jumun_time == o_time or jumun_time == o_time_p1 or jumun_time == o_time_m1 :         ## 주문 시간을 비교해서 같은 놈을 찾음
                        res = 1

        if res == 1 :                                                   ## 주문내역이 있는 경우
            print(self.now(), "[MAIN] [res_check_jumun] ORDER RCV PROPERLY")
            self.check_jumun_times[slot] = 0

        elif res == 0 :                                                 ## 주문내역이 없는 경우
            if self.check_jumun_times[slot] == 5 :                            ## jumun receive 여부 3회까지 확인
                self.check_jumun_times[slot] = 0                              ## re init
                print(self.now(), "[MAIN] [res_check_jumun] ORDER RCV NOT PROPERTY : END")

                if self.check_jumun[slot][4] == 9 :                     ## item find를 통해 buy 하는 경우
                    self.sig_worker_resume.emit(slot)                      ## worker lock 해제
                    self.item_finder_req = 0
                    self.item_slot[slot] = 0                            ## slot 해제
                    self.reply_buy.emit(1)                              ## 주문이 안들어 갔으므로 item finder 재 기동

                else :
                    if self.set_pause(int(slot)) == 1 :
                        self.table_summary.item(int(slot), 0).setBackground(QtGui.QColor(255,255,0))
                        self.sig_timer_paused.emit(slot)
            
            else :
                print(self.now(), "[MAIN] [res_check_jumun] ORDER RCV NOT PROPERTY : ", self.check_jumun_times[slot])
                self.check_jumun_times[slot] = self.check_jumun_times[slot] + 1
                QtTest.QTest.qWait(500)                                 ## 100 ms delay
                self.func_check_jumun(item_code, slot)                  ## re-check jumun
        
    def ORDER_SELL(self, item_code, qty, price) :
        # order = self.kiwoom.dynamicCall("SendOrder(QString, QString, QString, int, QString, int, int, QString, QString)",
        #              ["ORDER_SELL", "0101", ACCOUNT, 2, item_code, qty, price, "00", ""])
        order = self.kiwoom.dynamicCall("SendOrder(QString, QString, QString, int, QString, int, int, QString, QString)",
                     ["ORDER_SELL", "0101", ACCOUNT, 2, item_code, qty, 0, "03", ""])             
                    #  [rqname, screen_no, ACCOUNT, order_type, item_code, qty, price, hogagb, orgorderno])
        if order == 0 :
            print(self.now(), "[MAIN] [ORDER_SELL] : ", item_code, qty, price)
    ## 매수 ##
    def func_ORDER_BUY(self) :
        try:
            item_code = self.code_edit.text()

            already = self.which_thread(item_code)[0]
            th_num = self.which_thread(item_code)[1]

            qty = int(self.buy_sell_count.text())
            price = int(self.wid_sell_price.text())

            print("main already : ", already)

            print(self.now(), "[MAIN] [func_ORDER_BUY] : ", item_code, qty, price, th_num)

            temp = {}
            temp['autoTrade'] = 0
            temp['item_code'] = item_code

            if self.item_finder_req == 1 :          ## item finder의 요청에 의해 구매하는 경우
                temp['orderType'] = 9
            
            else :
                if already == 0 :                   ## 신규 item manual BUY
                    temp['orderType'] = 5
                elif already == 1 :                 ## 기존 item manual BUY
                    temp['orderType'] = 6

            temp['qty'] = qty
            temp['price'] = price
            temp['deposit'] = int(self.wid_show_deposit_d2.text())
            temp['timezone'] = self.timezone

            # temp['th_num'] = th_num
            
            self.item_slot[th_num] = item_code      ## slot assign

            # self.real_dict.emit(temp)

            print("main to worker : ", th_num)

            if th_num == 0 :
                self.test_dict0.emit(temp)
            elif th_num == 1 :
                self.test_dict1.emit(temp)
            elif th_num == 2 :
                self.test_dict2.emit(temp)
            elif th_num == 3 :
                self.test_dict3.emit(temp)
            elif th_num == 4 :
                self.test_dict4.emit(temp)
            elif th_num == 5 :
                self.test_dict5.emit(temp)
            elif th_num == 6 :
                self.test_dict6.emit(temp)
            elif th_num == 7 :
                self.test_dict7.emit(temp)
            elif th_num == 8 :
                self.test_dict8.emit(temp)
            elif th_num == 9 :
                self.test_dict9.emit(temp)

            elif th_num == 10 :
                self.test_dict10.emit(temp)
            elif th_num == 11 :
                self.test_dict11.emit(temp)
            elif th_num == 12 :
                self.test_dict12.emit(temp)
            elif th_num == 13 :
                self.test_dict13.emit(temp)
            elif th_num == 14 :
                self.test_dict14.emit(temp)

        except Exception as e:
            print(e)
            pass
    ## 매도 ##
    def func_ORDER_SELL(self) :
        try:
            item_code = self.code_edit.text()
            th_num = self.which_thread(item_code)[1]
            own_count = int(self.table_summary.item(th_num, 2).text())
            qty = int(self.buy_sell_count.text())
            # price = self.wid_buy_price.text()
            price = self.wid_sell_price.text()

            temp = {}
            temp['autoTrade'] = 0
            temp['item_code'] = item_code
            temp['deposit'] = int(self.wid_show_deposit_d2.text())

            if qty > own_count :
                print(self.now(), "[MAIN] [func_ORDER_SELL] : SELL Qty Exceed")
                
            elif qty < own_count :
                temp['orderType'] = 7
                
            elif qty == own_count :
                temp['orderType'] = 8
                
            temp['qty'] = qty
            temp['price'] = price
            temp['timezone'] = self.timezone
            # temp['th_num'] = th_num

            # self.real_dict.emit(temp)

            if th_num == 0 :
                self.test_dict0.emit(temp)
            elif th_num == 1 :
                self.test_dict1.emit(temp)
            elif th_num == 2 :
                self.test_dict2.emit(temp)
            elif th_num == 3 :
                self.test_dict3.emit(temp)
            elif th_num == 4 :
                self.test_dict4.emit(temp)
            elif th_num == 5 :
                self.test_dict5.emit(temp)
            elif th_num == 6 :
                self.test_dict6.emit(temp)
            elif th_num == 7 :
                self.test_dict7.emit(temp)
            elif th_num == 8 :
                self.test_dict8.emit(temp)
            elif th_num == 9 :
                self.test_dict9.emit(temp)

            elif th_num == 10 :
                self.test_dict10.emit(temp)
            elif th_num == 11 :
                self.test_dict11.emit(temp)
            elif th_num == 12 :
                self.test_dict12.emit(temp)
            elif th_num == 13 :
                self.test_dict13.emit(temp)
            elif th_num == 14 :
                self.test_dict14.emit(temp)
            
            print(self.now(), "[MAIN] [func_ORDER_SELL] : ", item_code, qty, price, th_num)

        except Exception as e:
            print(e)

    def func_restart_check(self, th_num, item_code) :
        print("func restart check : ", item_code)
        rqname = "RESET_" + str(th_num) + '_' + item_code

        self.reset_time = self.reset_time + 1
        self.kiwoom.dynamicCall("SetInputValue(QString, QString)", "계좌번호", ACCOUNT)
        self.kiwoom.dynamicCall("SetInputValue(QString, QString)", "비밀번호", PASSWORD)
        self.kiwoom.dynamicCall("CommRqData(QString, QString, int, QString)", rqname, "opw00018", 0, self.reset_time)       # 잔고 출력

        # print(now, "[MAIN]", "[func_restart_check] ORDER COMPLETE")

    def func_RESET_Items(self, rqname, trcode, recordname, slot, code) :
        print("func RESET Items : ", slot, code)
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

        che_dict = {}
        che_dict['th_num'] = slot
        che_dict['item_code'] = item_code
        che_dict['res'] = 1
        self.che_dict.emit(che_dict)

    def func_GET_Chejan_data(self, fid):
        ret = self.kiwoom.dynamicCall("GetChejanData(int)", fid)
        return ret
    def func_RECEIVE_Chejan_data(self, gubun, item_cnt, fid_list):
        order_id = item_code = item_name = trade_price = trade_amount = remained = trade_time = 'n'
        if gubun == "0" :       
            order_id = self.func_GET_Chejan_data(9203)              # 주문번호
            item_code = self.func_GET_Chejan_data(9001)             # 종목코드
            item_name = self.func_GET_Chejan_data(302)              # 종목명
            trade_amount = self.func_GET_Chejan_data(911)           # 체결량
            remained = self.func_GET_Chejan_data(902)               # 미체결
            trade_time = self.func_GET_Chejan_data(908)             # 주문체결시간

            self.func_GET_Ordering(self.today)                           ## 주문상황을 실시간으로 반영

            # 데이터가 여러번 표시되는 것이 아니라 다 받은 후 일괄로 처리되기 위함
            if remained == '0':         # 전수체결시
                item_code = item_code.replace('A', '').strip()
                # print(now, "[MAIN]", "CHE RECEIVE : ", item_code)

                # if item_code == self.buying_item :              ## item find를 통해 구매한 내역일 경우 item finder에 finish signal send
                #     self.reply_buy.emit(1)

                timestamp = self.func_GET_CurrentTime()
                
                print(self.now(), "[MAIN] [체결완료] : ", order_id, item_code, trade_amount)
                orderType = self.func_GET_db_item(item_code, 3)
                th_num = self.which_thread(item_code)[1]
                if orderType != "none" :
                    if orderType == 1 :
                        if self.DELETE_Table_Summary_item(th_num) == 0 :        ## table의 데이터를 다 지웠을 경우 0
                            self.func_restart_check(th_num, item_code)

                    elif orderType == 2 :
                        if self.DELETE_Table_Summary_item(th_num) == 0 :
                            self.func_restart_check(th_num, item_code)

                    elif orderType == 3 :                                   ## Full Sell 일 경우
                        self.item_slot[th_num] = 0      ## unassign slot
                        print("chajan : ", orderType, th_num, self.item_slot)
                        if self.DELETE_Table_Summary_item(th_num) == 0 :    ## table data 삭제
                            che_dict = {}
                            che_dict['th_num'] = th_num
                            che_dict['item_code'] = item_code
                            che_dict['res'] = 1
                            self.che_dict.emit(che_dict)                    ## 결과 전송

                    elif orderType == 4 :
                        if self.DELETE_Table_Summary_item(th_num) == 0 :
                            self.func_restart_check(th_num, item_code)

                    elif orderType == 5 :                                   ## BUY NEW(manual)
                        if self.DELETE_Table_Summary_item(th_num) == 0 :
                            self.func_restart_check(th_num, item_code)
                            self.SetRealReg("0101", item_code, "41", "1")      ## 실시간 데이터 수신 등록

                            

                    elif orderType == 6 :       ## gi buy (manual)
                        if self.DELETE_Table_Summary_item(th_num) == 0 :        ## table의 데이터를 다 지웠을 경우 0
                            self.func_restart_check(th_num, item_code)

                    elif orderType == 7 :       ## sell(manual)
                        if self.DELETE_Table_Summary_item(th_num) == 0 :        ## table의 데이터를 다 지웠을 경우 0
                            self.func_restart_check(th_num, item_code)

                    elif orderType == 8 :       ## manual Sell Full
                        self.item_slot[th_num] = 0      ## unassign slot

                        if self.DELETE_Table_Summary_item(th_num) == 0 :
                            che_dict = {}
                            che_dict['th_num'] = th_num
                            che_dict['item_code'] = item_code
                            che_dict['res'] = 1
                            self.che_dict.emit(che_dict)        ## 결과 
                    
                    elif orderType == 9 :       ## new buy by item finding
                        self.reply_buy.emit(1)
                        self.item_finder_req = 0

                        if self.DELETE_Table_Summary_item(th_num) == 0 :
                            self.func_restart_check(th_num, item_code)
                            self.SetRealReg("0101", item_code, "41", "1")      ## 실시간 데이터 수신 등록

                            

                    self.load_etc_data()

    def func_GET_Deposit(self) :
        self.kiwoom.dynamicCall("SetInputValue(QString, QString)", "계좌번호", ACCOUNT)
        self.kiwoom.dynamicCall("SetInputValue(QString, QString)", "비밀번호", PASSWORD)
        self.kiwoom.dynamicCall("CommRqData(QString, QString, int, QString)", "GET_Deposit", "opw00005", 0, "0104")
        # self.kiwoom.dynamicCall("CommRqData(QString, QString, int, QString)", "GET_Deposit", "opw00001", 0, "0104")       ## 모의 계좌
    def func_SHOW_Deposit(self, rqname, trcode, recordname) :
        # deposit = self.kiwoom.dynamicCall("GetCommData(QString, QString, int, QString)", trcode, recordname, 0, "예수금")
        # d_1 = self.kiwoom.dynamicCall("GetCommData(QString, QString, int, QString)", trcode, recordname, 0, "d+1추정예수금")
        # d_2 = self.kiwoom.dynamicCall("GetCommData(QString, QString, int, QString)", trcode, recordname, 0, "d+2추정예수금")
        deposit = self.kiwoom.dynamicCall("GetCommData(QString, QString, int, QString)", trcode, recordname, 0, "예수금")
        d_1 = self.kiwoom.dynamicCall("GetCommData(QString, QString, int, QString)", trcode, recordname, 0, "예수금D+1")
        d_2 = self.kiwoom.dynamicCall("GetCommData(QString, QString, int, QString)", trcode, recordname, 0, "예수금D+2")
        # orderable_money = self.kiwoom.dynamicCall("GetCommData(QString, QString, int, QString)", trcode, recordname, 0, "주문가능현금")

        self.wid_show_deposit.setText(str('{0:,}'.format(int(deposit))))
        self.wid_show_deposit_d1.setText(str('{0:,}'.format(int(d_1))))
        self.wid_show_deposit_d2.setText(str(int(d_2)))

        self.set_deposit = 1

    def func_GET_DailyProfit(self, index) :
        if index == 0:
            year = strftime("%Y", localtime())
            month = strftime("%m", localtime())

            start_day = year + month + "01"
        
        elif index == 1:
            start_day = self.input_ds_start.text()
            end_day = self.input_ds_end.text()

        self.kiwoom.dynamicCall("SetInputValue(QString, QString)", "계좌번호", ACCOUNT)
        self.kiwoom.dynamicCall("SetInputValue(QString, QString)", "시작일자", start_day)
        self.kiwoom.dynamicCall("SetInputValue(QString, QString)", "종료일자", self.today)
        self.kiwoom.dynamicCall("CommRqData(QString, QString, int, QString)", "GET_DailyProfit", "opt10074", 0, "0101")

        self.show_ds_start.setText(start_day)
        self.show_ds_end.setText(self.today)
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

                self.func_SET_TableData(4, i, 0, date.strip(), 0)
                self.func_SET_TableData(4, i, 1, total_buy.strip(), 0)
                self.func_SET_TableData(4, i, 2, total_sell.strip(), 0)

                if int(profit) == 0 :
                    self.func_SET_TableData(4, i, 3, profit.strip(), 0)
                elif int(profit) > 0 :
                    self.func_SET_TableData(4, i, 3, profit.strip(), 1)
                elif int(profit) < 0 :
                    self.func_SET_TableData(4, i, 3, profit.strip(), 2)

            except :
                pass

    def func_GET_Ordering(self, date):
        self.kiwoom.dynamicCall("SetInputValue(QString, QString)", "주문일자", date)
        self.kiwoom.dynamicCall("SetInputValue(QString, QString)", "계좌번호", ACCOUNT)
        self.kiwoom.dynamicCall("SetInputValue(QString, QString)", "비밀번호", PASSWORD)
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

            # hoga_buy = self.table_summary.item(row, 5).text()
            own_qty = self.table_summary.item(row, 2).text()
            hoga_sell = self.table_summary.item(row, 5).text()
            hoga_buy = self.table_summary.item(row, 5).text()

            self.buy_sell_count.setText(str(int(own_qty)))
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
        # numStocks = self.kiwoom.dynamicCall("GetCommData(QString, QString, int, QString)", trcode, recordname, 0, "상장주식")
        # prices = self.kiwoom.dynamicCall("GetCommData(QString, QString, int, QString)", trcode, recordname, 0, "시가")
        percent = self.kiwoom.dynamicCall("GetCommData(QString, QString, int, QString)", trcode, recordname, 0, "등락율")
        # per = self.kiwoom.dynamicCall("GetCommData(QString, QString, int, QString)", trcode, recordname, 0, "PER")
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
    def check_real(self, data) :
        self.SetRealRemove("ALL", "ALL")
        for i in range(NUM_SLOT) :
            if self.item_slot[i] != 0 :
                self.SetRealReg("0101", self.item_slot[i], "41", "1")      ## 실시간 데이터 수신 등록

    @pyqtSlot(int)
    def refresh_status(self, data) :
        ref_time = self.func_GET_CurrentTime2()
        self.load_etc_data()
        self.wid_refresh_order.setText(ref_time)

        print("refresh status")
        print(self.item_slot)

        for i in range(NUM_SLOT) :
            item_temp = self.table_summary.item(i, 0)
            print(i, ' : ', self.item_slot[i], ' : ', item_temp)

            if item_temp is None and self.item_slot[i] != 0 :
                rqname = "RSLOT_" + str(i) + '_' + str(self.item_slot[i])
                self.reset_time = self.reset_time + 1
                self.kiwoom.dynamicCall("SetInputValue(QString, QString)", "계좌번호", ACCOUNT)
                self.kiwoom.dynamicCall("SetInputValue(QString, QString)", "비밀번호", PASSWORD)
                self.kiwoom.dynamicCall("CommRqData(QString, QString, int, QString)", rqname, "opw00018", 0, self.reset_time)       # 잔고 출력
    
    def func_RESET_Slots(self, rqname, trcode, recordname, slot, code) :
        print("func RESET Slots : ", slot, code)
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

    @pyqtSlot(int)
    def min_check_jumun(self, data) :
        conn = sqlite3.connect("item_status.db")
        cur = conn.cursor()
        sql = "select code from STATUS where ordered=1"
        cur.execute(sql)
        rows = cur.fetchall()
        conn.close()

        for i in range(len(rows)) :
            temp_slot = self.which_thread(rows[i][0])[1]
            if self.paused[temp_slot] == 0 :                ## pause status
                self.first_rcv_jumun_check_2(temp_slot, rows[i][0])
                QtTest.QTest.qWait(350)

    @pyqtSlot(int)
    def timer_con_finish(self, data) :
        print("1. TIMER CONNECTED")
        self.func_GET_Deposit()

        while True :
            if self.set_deposit == 1:
                self.set_deposit = 0
                break
            QtTest.QTest.qWait(100)

        self.func_start_check()          # Aloha

    def event_connect(self, err_code):
        timestamp = self.func_GET_CurrentTime()
        self.wid_login.setText("Login : " + timestamp)
        
        if err_code == 0:
            self.timer = module_timer.Timer()
            self.timer.timer_connected.connect(self.timer_con_finish)
            self.timer.cur_time.connect(self.update_times)
            self.timer.check_slot.connect(self.check_slot)
            self.timer.sig_main_check_jumun.connect(self.min_check_jumun)
            self.timer.check_real.connect(self.check_real)
            self.timer.req_buy.connect(self.auto_buy)
            self.timer.refresh_status.connect(self.refresh_status)
            self.timer.release_paused.connect(self.release_paused)
            self.res_check_slot.connect(self.timer.res_check_slot)
            self.sig_timer_paused.connect(self.timer.rcv_paused)
            self.reply_buy.connect(self.timer.reply_buy)
            self.timer.start()
            
        else:
            print(self.now(), "[MAIN] Login Failed")
            try :
                self.kiwoom.dynamicCall("CommConnect()")        ## aloha
            except :
                pass
    
    @pyqtSlot(int)
    def release_paused(self, data) :
        if self.unset_pause(int(data)) == 1 :
            self.table_summary.item(int(data), 0).setBackground(QtGui.QColor(255,255,255))
            self.sig_worker_resume.emit(int(data))

    def set_pause(self, slot) :
        self.paused[slot] = 1
        return 1

    def unset_pause(self, slot) :
        self.paused[slot] = 0
        return 1

    def func_SET_tableSUMMARY(self):
        self.table_summary.setRowCount(NUM_SLOT)
        self.table_summary.setColumnCount(SUMMARY_COL_CNT)
        self.table_summary.resizeRowsToContents()

        for i in range(SUMMARY_COL_CNT):
            self.table_summary.setColumnWidth(i, 90)
        
        self.table_summary.setColumnWidth(1, 150)
        
        self.table_summary.verticalHeader().setVisible(False)
        self.table_summary.verticalHeader().setDefaultSectionSize(1)

        for i in range(len(SUMMARY_TITLES)) :
            self.table_summary.setHorizontalHeaderItem(i, QTableWidgetItem(SUMMARY_TITLES[i]))    
        
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

        self.table_order.setColumnWidth(4, 160)
        self.table_order.setColumnWidth(5, 80)
        self.table_order.setColumnWidth(6, 80)
        self.table_order.setColumnWidth(7, 80)

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
        col_count = 4

        self.table_dailyprofit.setRowCount(row_count)
        self.table_dailyprofit.setColumnCount(col_count)
        self.table_dailyprofit.resizeRowsToContents()

        for i in range(col_count):
            self.table_dailyprofit.setColumnWidth(i, 125)

        self.table_dailyprofit.verticalHeader().setVisible(False)
        self.table_dailyprofit.verticalHeader().setDefaultSectionSize(1)
        self.table_dailyprofit.setHorizontalHeaderItem(0, QTableWidgetItem("일자"))
        self.table_dailyprofit.setHorizontalHeaderItem(1, QTableWidgetItem("매수금액"))
        self.table_dailyprofit.setHorizontalHeaderItem(2, QTableWidgetItem("매도금액"))
        self.table_dailyprofit.setHorizontalHeaderItem(3, QTableWidgetItem("매도손익"))
        # self.table_dailyprofit.setHorizontalHeaderItem(4, QTableWidgetItem("수수료"))
        # self.table_dailyprofit.setHorizontalHeaderItem(5, QTableWidgetItem("세금"))
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
    def DisConnectRealData(self, screen_no):
        self.kiwoom.dynamicCall("DisConnectRealData(QString)", screen_no)

    def receive_tr_data(self, screen_no, rqname, trcode, recordname, prev_next, data_len, err_code, msg1, msg2):
        # print("[MAIN] [receive_tr_data] : ", rqname)

        if "RESET_" in rqname:
            item_slot = int(rqname[6:7])
            item_code = rqname[8:]
            self.func_RESET_Items(rqname, trcode, recordname, item_slot, item_code)
        
        elif "RSLOT_" in rqname:
            item_slot = int(rqname[6:7])
            item_code = rqname[8:]
            self.func_RESET_Slots(rqname, trcode, recordname, item_slot, item_code)

        elif "check_deposit" in rqname :
            item_code = rqname[0:6]
            item_slot = rqname[6:7]
            self.check_deposit_2(rqname, trcode, recordname, item_slot, item_code)
        
        elif "jan_check" in rqname :
            item_code = rqname[0:6]
            item_slot = rqname[6:7]
            self.result_get_hoga(rqname, trcode, recordname, item_code, item_slot)

        elif "check_jumun" in rqname :
            item_code = rqname[0:6]
            item_slot = rqname[6:7]
            self.res_check_jumun(rqname, trcode, recordname, item_code, item_slot)

        elif "first_jumun_check" in rqname :
            item_code = rqname[0:6]
            item_slot = rqname[6:7]
            self.res_first_check_jumun(rqname, trcode, recordname, item_code, item_slot)

        elif rqname == "SET_hoga":
            self.SET_hoga(rqname, trcode, recordname)

        elif rqname == "SET_hoga2":
            self.SET_hoga2(rqname, trcode, recordname)


        elif rqname == "GET_DailyProfit":
            self.func_SHOW_DailyProfit(rqname, trcode, recordname)
        elif rqname == "SETTING":
            self.func_SET_Items(rqname, trcode, recordname)
        elif rqname == "GET_Deposit":
            self.func_SHOW_Deposit(rqname, trcode, recordname)

        elif rqname == "GET_ItemInfo":
            self.func_SHOW_ItemInfo(rqname, trcode, recordname)

        elif rqname == "GET_ItemInfo_test":
            self.func_SHOW_ItemInfo_test(rqname, trcode, recordname)

        elif rqname == "GET_Ordering":
            self.func_SHOW_Ordering(rqname, trcode, recordname)
        elif rqname == "opw00018_req":
            self.func_SHOW_CheckBalance(rqname, trcode, recordname)
    
    def which_slot(self, item_code) :
        slot = -1

        for i in range(NUM_SLOT) :
            if self.item_slot[i] == item_code :
                slot = i
                break
        
        return slot

    def func_SET_db_table(self) :
        conn = sqlite3.connect("item_status.db")
        cur = conn.cursor()
        sql = "create table if not exists STATUS (code text, step integer, ordered integer, orderType integer, perlow real)"
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
            elif col == 4:      # get perlow
                sql = "select perlow from STATUS where code = ?"
                cur.execute(sql, [code])

            row = cur.fetchone()
            conn.close()

            if row is None:
                return "none"
            else:
                return row[0]
    def func_INSERT_db_item(self, code, step, ordered, orderType, perlow):
        conn = sqlite3.connect("item_status.db")
        cur = conn.cursor()
        sql = "insert into STATUS (code, step, ordered, orderType, perlow) values(:CODE, :STEP, :ORDERED, :ORDERTYPE, :PERLOW)"
        cur.execute(sql, {"CODE" : code, "STEP" : step, "ORDERED" : ordered, "ORDERTYPE" : orderType, "PERLOW" : perlow})
        conn.commit()
        conn.close()
        print(self.now(), "[MAIN] [func_INSERT_db_item] : INSERTED")
    def func_DELETE_db_item(self, code):
        conn = sqlite3.connect("item_status.db")
        cur = conn.cursor()
        sql = "delete from STATUS where code = :CODE"
        cur.execute(sql, {"CODE" : code})
        conn.commit()
        conn.close()
        print(self.now(), "[MAIN] [func_DELETE_db_item] : DELETED")

        return 1

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

    def which_thread_2(self, item_code) :
        th_num = [0, 100]

        ## 기존에 할당되어 있는지 우선 검색
        for i in range(NUM_SLOT) :
            if item_code == self.item_slot[i] :
                th_num[0] = 1
                th_num[1] = i
                break

        return th_num
        
    def now(self) :
        return datetime.datetime.now()
if __name__=="__main__":
    app = QApplication(sys.argv)
    app.setStyle(QStyleFactory.create('Fusion')) # --> 없으면, 헤더색 변경 안됨.
    # print(now, "[MAIN]", sys.argv)
    myWindow = Kiwoom()
    myWindow.show()
    app.exec_()
    