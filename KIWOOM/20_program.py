import sys
import sqlite3
import time
import math
from time import localtime, strftime
import pandas as pd

from PyQt5.QtWidgets import *
from PyQt5.QAxContainer import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5 import QtTest, QtCore, QtWidgets, uic, QtGui
import module_timer
import module_get_summary
import module_item_finder

form_class = uic.loadUiType("interface.ui")[0]
ACCOUNT = "8137639811"
PASSWORD = "6458"
TAX = 0.0025
FEE_BUY = 0.0035
FEE_SELL = 0.0035
GOAL_PER = -0.01
STEP_LIMIT = 5

MAKE_ORDER = 0

for i in range(10) :
    globals()['DF_item{}'.format(i)] = pd.DataFrame(columns = ['code', '%', 'm_1', 'm_2', 'm_3', 'm_4', 'm_5', 'm_6', 'm_7', 'm_8', 'm_9', 'm_10'])
    globals()['save_times{}'.format(i)] = 0
    globals()['elapsed_min{}'.format(i)] = 0

class Kiwoom(QMainWindow, form_class):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.kiwoom = QAxWidget()
        self.kiwoom.setControl("KHOPENAPI.KHOpenAPICtrl.1")

        self.comm_connect()       # Aloha
        
        self.kiwoom.OnEventConnect.connect(self.event_connect)
        self.kiwoom.OnReceiveTrData.connect(self.receive_tr_data)
        self.kiwoom.OnReceiveRealData.connect(self.receive_real_data)
        self.kiwoom.OnReceiveChejanData.connect(self.func_RECEIVE_Chejan_data)

        self.init_ENV()

    def init_ENV(self) :
        ## flag setting
        self.cnt_call_hoga = 0
        self.cnt_tab_history = 0
        self.flag_ItemInfo_click = 0
        self.flag_HistoryData_Auto = 0
        self.stay_print_time = {}
        self.status_print_time = {}     # judge 판단 후 이상없을 시 현상황 print를 위한 dict 자료형 init
        self.item_codes = []
        self.flag_checking = 0

        self.func_SET_db_table()        # db table 생성
        self.df_history = pd.DataFrame(columns = ['time', 'type', 'T_ID', 'Code', 'Name', 'Qty', 'Price', 'Req_ID'])

        ## button 동작 binding
        self.btn_ITEM_LOOKUP.clicked.connect(self.func_GET_ItemInfo)
        self.btn_BUY.clicked.connect(self.func_ORDER_BUY_click)
        self.btn_SELL.clicked.connect(self.func_ORDER_SELL_click)
        self.btn_TEST.clicked.connect(self.btn_test)
        self.btn_TEST_2.clicked.connect(self.btn_test_2)
        self.btn_START.clicked.connect(self.func_start_check)
        self.btn_STOP.clicked.connect(self.func_stop_check)
        self.btn_HISTORY.clicked.connect(self.func_GET_TradeHistory)

        ## table setting
        self.func_SET_tableSUMMARY()        # monitoring table
        self.func_SET_tableHISTORY()        # history table
        self.func_SET_tableORDER()          # order 현황 table
        self.func_SET_tableDAILYSUMMARY()          # order 현황 table

    @pyqtSlot(str)
    def update_times(self, data) :
        self.text_edit4.setText(data)
    @pyqtSlot(str)
    def item_finder_messages(self, data):
        self.text_edit.append(data)
    @pyqtSlot(dict)
    def item_finder_items(self, data):
        new_items = pd.DataFrame.from_dict(data)
        print(new_items)

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
        if col == 1:        # get step
            sql = "select step from STATUS where code = ?"
            cur.execute(sql, [code])
        elif col == 2:      # get ordered
            sql = "select ordered from STATUS where code = ?"
            cur.execute(sql, [code])
        elif col == 3:      # get ordered
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
        print("data INSERTED")
    def func_UPDATE_db_item(self, code, col, data) :
        conn = sqlite3.connect("item_status.db")
        cur = conn.cursor()
        if col == 1:    # update step
            sql = "update STATUS set step = :DATA where code = :CODE"    
            cur.execute(sql, {"DATA" : data, "CODE" : code})
        elif col == 2:  # update ordered
            sql = "update STATUS set ordered = :DATA where code = :CODE"    
            cur.execute(sql, {"DATA" : data, "CODE" : code})
        elif col == 3:  # update orderType
            sql = "update STATUS set orderType = :DATA where code = :CODE"    
            cur.execute(sql, {"DATA" : data, "CODE" : code})
            #### type ####
            # 0 : normai(default)
            # 1 : 물타기
            # 2 : 수익실현 및 복구
            # 3 : full 매도
            # 4 : 존버
        elif col == 4:  # update trAmount
            sql = "update STATUS set trAmount = :DATA where code = :CODE"    
            cur.execute(sql, {"DATA" : data, "CODE" : code})

        conn.commit()
        conn.close()
        success = cur.rowcount
        # print("UPDATED")
        return success
    def func_DELETE_db_item(self, code):
        conn = sqlite3.connect("item_status.db")
        cur = conn.cursor()
        sql = "delete from STATUS where code = :CODE"
        cur.execute(sql, {"CODE" : code})
        conn.commit()
        conn.close()
        print("data DELETED")
    
    def func_GET_Ordering(self, today):
        print("GET Ordering")
        acc_no = ACCOUNT
        acc_pw = PASSWORD

        # today = "20200625"

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

            for i in range(data_cnt):
                print("i :", i)
                try:
                    order_id = self.kiwoom.dynamicCall("GetCommData(QString, QString, int, QString)", trcode, recordname, i, "주문번호")
                    item_code = self.kiwoom.dynamicCall("GetCommData(QString, QString, int, QString)", trcode, recordname, i, "종목번호")
                    item_name = self.kiwoom.dynamicCall("GetCommData(QString, QString, int, QString)", trcode, recordname, i, "종목명")
                    deal_type = self.kiwoom.dynamicCall("GetCommData(QString, QString, int, QString)", trcode, recordname, i, "주문구분")
                    order_time = self.kiwoom.dynamicCall("GetCommData(QString, QString, int, QString)", trcode, recordname, i, "주문시간")
                    order_amount = self.kiwoom.dynamicCall("GetCommData(QString, QString, int, QString)", trcode, recordname, i, "주문수량")
                    trade_amount = self.kiwoom.dynamicCall("GetCommData(QString, QString, int, QString)", trcode, recordname, i, "체결수량")
                    remained = self.kiwoom.dynamicCall("GetCommData(QString, QString, int, QString)", trcode, recordname, i, "주문잔량")

                    self.func_SET_TableData(3, i, 0, deal_type.strip(), 0)
                    self.func_SET_TableData(3, i, 1, order_id, 0)
                    self.func_SET_TableData(3, i, 2, order_time, 0)
                    self.func_SET_TableData(3, i, 3, item_code.replace('A', '').strip(), 0)
                    self.func_SET_TableData(3, i, 4, item_name.strip(), 0)
                    self.func_SET_TableData(3, i, 5, str(int(order_amount)), 0)
                    self.func_SET_TableData(3, i, 6, str(int(trade_amount)), 0)
                    if int(remained) > 0:
                        self.func_SET_TableData(3, i, 7, str(int(remained)), 1)
                    else :
                        self.func_SET_TableData(3, i, 7, str(int(remained)), 0)

                except:
                    pass
            
    def btn_test(self) :
        print("btn test")
        item_code = "005930"
        if self.func_UPDATE_db_item(item_code, 2, 11) == 1:       # ordered -> 0
            if self.func_UPDATE_db_item(item_code, 3, 11) == 1:       # orderType -> 0
                self.func_UPDATE_db_item(item_code, 4, 21)       # trAmount -> 0
        

    def btn_test_2(self):
        print("btn Test2 clicked")
        code = "015760"
        self.SetRealRemove("0101", code)
        
            

    def func_start_check(self) :
        self.flag_checking = 1
        ## history load
        today = self.func_GET_Today()
        self.flag_HistoryData_Auto = 1
        self.func_GET_TradeHistory(today)
        self.func_GET_Deposit()

        acc_no = ACCOUNT
        acc_pw = PASSWORD
        self.kiwoom.dynamicCall("SetInputValue(QString, QString)", "계좌번호", acc_no)
        self.kiwoom.dynamicCall("SetInputValue(QString, QString)", "비밀번호", acc_pw)
        self.kiwoom.dynamicCall("CommRqData(QString, QString, int, QString)", "SETTING", "opw00018", 0, "0101")

    def func_SET_Items(self, rqname, trcode, recordname):
        self.table_summary.clearContents()      ## table clear
        self.item_count = int(self.func_GET_RepeatCount(trcode, rqname))

        for i in range(self.item_count):
            item_code = self.kiwoom.dynamicCall("GetCommData(QString, QString, int, QString)", trcode, recordname, i, "종목번호").replace('A', '').strip()
            item_name = self.kiwoom.dynamicCall("GetCommData(QString, QString, int, QString)", trcode, recordname, i, "종목명").strip()
            owncount = self.kiwoom.dynamicCall("GetCommData(QString, QString, int, QString)", trcode, recordname, i, "보유수량")
            unit_price = self.kiwoom.dynamicCall("GetCommData(QString, QString, int, QString)", trcode, recordname, i, "매입가")

            self.func_SET_TableData(1, i, 0, item_code, 0)
            self.func_SET_TableData(1, i, 1, item_name, 0)
            self.func_SET_TableData(1, i, 2, str(int(owncount)), 0)
            self.func_SET_TableData(1, i, 3, str(round(float(unit_price), 1)), 0)

            step = self.func_GET_db_item(item_code, 1)
            if step == "none" :
                self.func_INSERT_db_item(item_code, 0, 0, 0, 0)       # db initialize
            else :
                self.func_SET_TableData(1, i, 13, str(step), 0)

        self.item_codes = []
        for i in range(self.item_count):
            code = self.table_summary.item(i, 0).text()
            self.SetRealReg("0101", code, "10", 1)      # Real Time Data Registration
            self.item_codes.append(code)

        for i in range(self.item_count) :
            code = self.table_summary.item(i, 0).text()
            self.status_print_time[code] = 0
            self.stay_print_time[code] = 0
        
        timestamp = self.func_GET_CurrentTime()
        self.text_edit.append(timestamp + "Monitoring START")

    def func_stop_check(self):
        # print("self : ", self.item_count, type(self.item_count))
        # for i in range(self.item_count) :
        #     code = self.table_summary.item(i, 0).text()
        #     self.SetRealRemove("0101", code)

        self.SetRealRemove("ALL", "ALL")

        timestamp = self.func_GET_CurrentTime()
        self.text_edit.append(timestamp + "Monitoring STOP")

        return 1

    def SetRealReg(self, screenNo, item_code, fid, realtype):
        self.kiwoom.dynamicCall("SetRealReg(QString, QString, QString, QString)", screenNo, item_code, fid, realtype)
    def SetRealRemove(self, screenNo, item_code):
        self.kiwoom.dynamicCall("SetRealRemove(QString, QString)", screenNo, item_code)

    ## 매수 ##
    def func_ORDER_BUY_click(self) :
        timestamp = self.func_GET_CurrentTime()
        self.text_edit.append(timestamp + "Clicked : BUY")
        try:
            item_code = self.code_edit.text()
            qty = int(self.buy_sell_count.text())
            price = self.wid_sell_price.text()

        except Exception as e:
            timestamp = self.func_GET_CurrentTime()
            self.text_edit.append(timestamp + str(e))
            pass

        self.func_ORDER_BUY_2(item_code, qty, price)
    def func_ORDER_BUY_auto(self, item_code, qty, price) :
        timestamp = self.func_GET_CurrentTime()
        self.text_edit.append(timestamp + "Auto : BUY " + item_code)

        item_code = item_code.replace('A', '').strip()

        print("order buy")
        print("code : ", item_code)
        print("qty : ", qty)
        print("price : ", price)
        print("")

        try:
            # a = 0
            self.func_ORDER_BUY_2(item_code, qty, price)
            
        except Exception as e:
            timestamp = self.func_GET_CurrentTime()
            self.text_edit.append(timestamp + str(e))
    def func_ORDER_BUY_2(self, item_code, qty, price) :
        timestamp = self.func_GET_CurrentTime()
        self.text_edit.append(timestamp + "ORDER : BUY")

        rqname = "RQ_TEST"
        screen_no = "0101"
        acc_no = ACCOUNT
        order_type = 1
        hogagb = "00"
        orgorderno = ""
        order = self.kiwoom.dynamicCall("SendOrder(QString, QString, QString, int, QString, int, int, QString, QString)",
                     [rqname, screen_no, acc_no, order_type, item_code, qty, price, hogagb, orgorderno])
        self.func_UPDATE_db_item(item_code, 2, 1)       # 해당 item 의 현재 상태를 Trading으로 변환

    ## 매도 ##
    def func_ORDER_SELL_click(self) :
        timestamp = self.func_GET_CurrentTime()
        self.text_edit.append(timestamp + "Clicked : SELL")

        try:
            item_code = self.code_edit.text()
            qty = int(self.buy_sell_count.text())
            price = self.wid_buy_price.text()

        except Exception as e:
            timestamp = self.func_GET_CurrentTime()
            self.text_edit.append(timestamp + str(e))

        self.func_ORDER_SELL_2(item_code, qty, price)
    def func_ORDER_SELL_auto(self, item_code, qty, price) :
        timestamp = self.func_GET_CurrentTime()
        self.text_edit.append(timestamp + "Auto : SELL")

        item_code = item_code.replace('A', '').strip()

        print("order sell")
        print("code : ", item_code)
        print("qty : ", qty)
        print("price : ", price)
        print("")

        try:
            a = 0
            # self.func_ORDER_SELL_2(item_code, qty, price)
            
        except Exception as e:
            timestamp = self.func_GET_CurrentTime()
            self.text_edit.append(timestamp + str(e))
    def func_ORDER_SELL_2(self, item_code, qty, price) :
        timestamp = self.func_GET_CurrentTime()
        self.text_edit.append(timestamp + "ORDER : SELL")
        
        rqname = "RQ_TEST"
        screen_no = "0101"
        acc_no = ACCOUNT
        order_type = 2
        hogagb = "00"
        orgorderno = ""
        
        order = self.kiwoom.dynamicCall("SendOrder(QString, QString, QString, int, QString, int, int, QString, QString)",
                     [rqname, screen_no, acc_no, order_type, item_code, qty, price, hogagb, orgorderno])
        self.func_UPDATE_db_item(item_code, 2, 1)       # 해당 item 의 현재 상태를 Trading으로 변환

    def func_GET_Chejan_data(self, fid):
        ret = self.kiwoom.dynamicCall("GetChejanData(int)", fid)
        return ret
    def func_RECEIVE_Chejan_data(self, gubun, item_cnt, fid_list):
        order_id = item_code = item_name = trade_price = trade_amount = remained = trade_time = 'n'
        if gubun == "0" :       
            order_id = self.func_GET_Chejan_data(9203)      # 주문번호
            item_code = self.func_GET_Chejan_data(9001)     # 종목코드
            item_name = self.func_GET_Chejan_data(302)      # 종목명
            # trade_price = self.func_GET_Chejan_data(931)    # 체결단가
            trade_amount = self.func_GET_Chejan_data(911)   # 체결량
            remained = self.func_GET_Chejan_data(902)       # 미체결
            trade_time = self.func_GET_Chejan_data(908)      # 주문체결시간

            # 데이터가 여러번 표시되는 것이 아니라 다 받은 후 일괄로 처리되기 위함
            if remained == '0':         # 체결시
                self.func_stop_check()      ## checking stop

                self.text_edit.append("-- 체결완료 --")
                self.text_edit.append("체결시간 : " + trade_time)
                self.text_edit.append("주문번호 : " + order_id)
                self.text_edit.append("종목코드 : " + item_code)
                self.text_edit.append("종목명 : " + item_name)
                self.text_edit.append("체결량 : " + trade_amount)
                self.text_edit.append("미체결 : " + remained)
                self.text_edit.append("")

                ## 체결시 history table 갱신 수행
                today = self.func_GET_Today()
                self.flag_HistoryData_Auto = 1
                self.func_GET_TradeHistory(today)

                ## 체결시 db 갱신 수행
                item_code = item_code.replace('A', '').strip()
                step = self.func_GET_db_item(item_code, 1)

                ### db에 저장안된 item 일 경우 item 초기화
                if step == "none":
                    self.func_INSERT_db_item(item_code, 0, 0, 0, 0)

                ### db에 이미 저장되어 있는 item 일 경우
                else :
                    #### orderType 검사
                    orderType = self.func_GET_db_item(item_code, 3)

                    if orderType == 0 :             # normal trade
                        self.func_UPDATE_db_item(item_code, 2, 0)       # ordered -> 0

                    elif orderType == 1 :         # add water
                        if self.func_UPDATE_db_item(item_code, 2, 0) == 1:       # ordered -> 0
                            if self.func_UPDATE_db_item(item_code, 3, 0) == 1:       # orderType -> 0
                                new_step = step + 1
                                self.func_UPDATE_db_item(item_code, 1, new_step)

                    elif orderType == 2 :       # sell & buy 중 sell 완료
                        self.func_UPDATE_db_item(item_code, 3, 4)       # orderType -> 4

                    elif orderType == 3 :       # full sell
                        self.func_DELETE_db_item(item_code)

                    elif orderType == 4 :       # sellf & buy 중 buy 완료
                        if self.func_UPDATE_db_item(item_code, 2, 0) == 1:       # ordered -> 0
                            if self.func_UPDATE_db_item(item_code, 3, 0) == 1:       # orderType -> 0
                                self.func_UPDATE_db_item(item_code, 4, 0)       # trAmount -> 0


                # restart checking
                self.func_start_check()


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

        # str('{0:,}'.format())
        self.wid_show_deposit.setText(str('{0:,}'.format(int(deposit))))
        self.wid_show_deposit_d1.setText(str('{0:,}'.format(int(d_1))))
        self.wid_show_deposit_d2.setText(str('{0:,}'.format(int(d_2))))

    def func_GET_TradeHistory(self, date) :       # search history data manually
        if self.flag_HistoryData_Auto == 1:
            # print("auto here")
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
        self.kiwoom.dynamicCall("CommRqData(QString, QString, int, QString)", "opw00009_man", "opw00009", 0, "0101")
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

    def func_GET_ItemInfo(self, code):
        if self.flag_ItemInfo_click == 0:
            code = self.code_edit.text()
        else :
            code = code
            self.flag_ItemInfo_click = 0

        self.GET_hoga(code)

    def func_GET_ItemInfo_by_click(self, index) :
        row = index.row()
        try:
            item_code = self.table_summary.item(row, 0).text()
            item_code = item_code.replace("A", "")
            self.flag_ItemInfo_click = 1
            self.code_edit.setText(item_code.strip())
            self.func_GET_ItemInfo(item_code.strip())
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

        self.SetRealRemove("ALL", "ALL")
        if self.flag_checking == 1 :
            self.func_start_check()

    def func_GET_CurrentTime(self) :
        year = strftime("%Y", localtime())
        month = strftime("%m", localtime())
        day = strftime("%d", localtime())
        hour = strftime("%H", localtime())
        cmin = strftime("%M", localtime())
        sec = strftime("%S", localtime())

        now = "[" + year + "/" + month +"/" + day + " " + hour + ":" + cmin + ":" + sec + "] "

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
    ## [START] login ##
    def comm_connect(self):
        self.kiwoom.dynamicCall("CommConnect()")
        self.login_event_loop = QThread()
        self.login_event_loop.start()
    def event_connect(self, err_code):
        if err_code == 0:
            timestamp = self.func_GET_CurrentTime()
            self.text_edit.append(timestamp + "Login Complete")
            self.timer = module_timer.Timer()
            self.timer.cur_time.connect(self.update_times)
            self.timer.start()

            timestamp = self.func_GET_CurrentTime()
            self.text_edit.append(timestamp + "Timer Thread Started")
            self.login_event_loop.terminate()

            # self.func_start_check()          # Aloha
            
        else:
            print("Login Failed")
    ## [END] login ##
    def func_SET_tableSUMMARY(self):
        row_count = 5
        col_count = 14
        self.table_summary.setRowCount(row_count)
        self.table_summary.setColumnCount(col_count)
        self.table_summary.resizeRowsToContents()

        for i in range(col_count):
            self.table_summary.setColumnWidth(i, 100)
        
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
    def func_SET_tableDAILYSUMMARY(self):
        row_count = 0
        col_count = 6

        self.table_daily_summary.setRowCount(row_count)
        self.table_daily_summary.setColumnCount(col_count)
        self.table_daily_summary.resizeRowsToContents()

        for i in range(col_count):
            self.table_daily_summary.setColumnWidth(i, 100)

        self.table_daily_summary.verticalHeader().setVisible(False)
        self.table_daily_summary.verticalHeader().setDefaultSectionSize(1)
        self.table_daily_summary.setHorizontalHeaderItem(0, QTableWidgetItem("일자"))
        self.table_daily_summary.setHorizontalHeaderItem(1, QTableWidgetItem("매수금액"))
        self.table_daily_summary.setHorizontalHeaderItem(2, QTableWidgetItem("매도금액"))
        self.table_daily_summary.setHorizontalHeaderItem(3, QTableWidgetItem("매도손익"))
        self.table_daily_summary.setHorizontalHeaderItem(4, QTableWidgetItem("수수료"))
        self.table_daily_summary.setHorizontalHeaderItem(5, QTableWidgetItem("세금"))

    def func_SET_TableData(self, table_no, row, col, content, color):
        # summary table
        if table_no == 1:
            item = QTableWidgetItem(content)
            # item.setAlignment(QtCore.Qt.AlignHCenter | QtCore.Qt.AlignVCenter)
            item.setTextAlignment(4)    # 가운데 정렬
            if color == 1:
                item.setForeground(QBrush(Qt.red)) # 글자색
            elif color == 2:
                item.setForeground(QBrush(Qt.blue)) # 글자색
            self.table_summary.setItem(row, col, item)
        
        # history table
        if table_no == 2:
            item = QTableWidgetItem(content)
            item.setTextAlignment(4)    # 가운데 정렬
            self.table_history.setItem(row, col, item)

        # order table
        if table_no == 3:
            order = 1
            item = QTableWidgetItem(content)
            item.setTextAlignment(4)    # 가운데 정렬
            self.table_order.setItem(row, col, item)
    def receive_tr_data(self, screen_no, rqname, trcode, recordname, prev_next, data_len, err_code, msg1, msg2):

        # print("data received")
        # comp_str = "GET_Item_Price"

        # if comp_str in rqname:
        #     self.SET_hoga(rqname, trcode, recordname)

        if rqname == "SET_hoga":
            self.SET_hoga(rqname, trcode, recordname)

        if rqname == "SETTING":
            self.func_SET_Items(rqname, trcode, recordname)
        if rqname == "GET_Deposit":
            self.func_SHOW_Deposit(rqname, trcode, recordname)

        if rqname == "GET_ItemInfo":
            self.func_SHOW_ItemInfo(rqname, trcode, recordname)

        if rqname == "GET_Ordering":
            self.func_SHOW_Ordering(rqname, trcode, recordname)

        if rqname == "opw00018_req":
            # print("DATA : CHECK BALANCE")
            self.func_SHOW_CheckBalance(rqname, trcode, recordname)

        if rqname == "opw00009_man":
            self.func_SHOW_TradeHistory(rqname, trcode, recordname)
    def receive_real_data(self, code, real_type, real_data): 
        print("receive REAL DATA : ", code)

        val = self.kiwoom.dynamicCall("GetCommRealData(QString, int)", code, 10)
        price_buy = self.kiwoom.dynamicCall("GetCommRealData(QString, int)", code, 27)
        price_sell = self.kiwoom.dynamicCall("GetCommRealData(QString, int)", code, 28)

        if val != '' :
            for i in range(len(self.item_codes)) :
                if code == self.item_codes[i]:
                    if self.func_GET_db_item(code, 2) == 1:     # status : trading
                        self.table_summary.item(i, 0).setBackground(QtGui.QColor(0,255,0))
                        if self.func_GET_db_item(code, 3) == 4:         # sell & buy 중 buy 단계인 경우
                            buy_qty = self.func_GET_db_item(code, 4)

                            self.func_UPDATE_db_item(item_code, 3, 0)       # orderType -> 0

                            # self.func_ORDER_BUY_auto(code, buy_qty, price_buy)

                    else :
                        self.table_summary.item(i, 0).setBackground(QtGui.QColor(255,255,255))
                        val = val.replace('+', '').replace('-', '').strip()
                        self.func_SET_TableData(1, i, 4, val, 0)
                        price_buy = price_buy.replace('+', '').replace('-', '').strip()
                        price_sell = price_sell.replace('+', '').replace('-', '').strip()
                        self.func_SET_TableData(1, i, 5, price_buy, 0)
                        self.func_SET_TableData(1, i, 6, price_sell, 0)
                        # self.func_SET_TableData(1, i, 6, price_sell.replace('+', '').replace('-', '').strip(), 0)
                        owncount = int(self.table_summary.item(i, 2).text())
                        unit = float(self.table_summary.item(i, 3).text())

                        total_purchase = owncount * unit
                        self.func_SET_TableData(1, i, 7, str(total_purchase), 0)
                        
                        total_evaluation = owncount * float(val)
                        self.func_SET_TableData(1, i, 8, str(total_evaluation), 0)

                        temp_total = total_evaluation - total_purchase
                        self.func_SET_TableData(1, i, 9, str(temp_total), 0)

                        fee_buy = FEE_BUY * total_purchase
                        fee_sell = FEE_SELL * total_evaluation
                        tax = TAX * total_evaluation
                        total_fee = round((fee_buy + fee_sell + tax), 1)
                        self.func_SET_TableData(1, i, 10, str(total_fee), 0)

                        total_sum = total_evaluation - total_purchase - total_fee
                        self.func_SET_TableData(1, i, 11, str(int(total_sum)), 0)

                        percent = round((total_sum / total_purchase) * 100, 1)
                        if percent > 0:
                            self.func_SET_TableData(1, i, 12, str(percent), 1)
                        elif percent < 0:
                            self.func_SET_TableData(1, i, 12, str(percent), 2)
                        else :
                            self.func_SET_TableData(1, i, 12, str(percent), 0)

                        ################## judgement ###################
                        item_code = code
                        step = self.func_GET_db_item(item_code, 1)
                        self.func_SET_TableData(1, i, 13, str(step), 0)


                        # Add Water
                        if percent < -2 and step < STEP_LIMIT :
                            timestamp = self.func_GET_CurrentTime()
                            self.text_edit.append(timestamp + " " + item_code + " JUDGE : 물타기")
                            
                            V = int(price_buy)          # 매도 최우선가
                            A = total_purchase          # 총 매입금액
                            B = total_evaluation        # 총 평가금액
                            T = TAX
                            FB = FEE_BUY
                            FS = FEE_SELL
                            P = GOAL_PER

                            buy_qty = math.ceil((B-A-B*T-A*FB-B*FS-A*P) / (V*P + V*T + FB + FS))

                            if self.func_UPDATE_db_item(item_code, 2, 1) == 1:       ## ordered 변경(-> 1)
                                if self.func_UPDATE_db_item(item_code, 3, 1) == 1:       ## orderType을 물타기(1) 로 변경
                                    if MAKE_ORDER == 1:
                                        self.func_ORDER_BUY_auto(item_code, buy_qty, V)    # make order

                        # Sell & Buy
                        if percent > 2 and step < STEP_LIMIT :
                            timestamp = self.func_GET_CurrentTime()
                            self.text_edit.append(timestamp + " " + item_code + " JUDGE : 수익실현 및 복구")
                            sell_qty = int(owncount / 2)
                            price = int(price_sell)

                            if self.func_UPDATE_db_item(item_code, 2, 1) == 1:       ## ordered 변경(-> 1)
                                if self.func_UPDATE_db_item(item_code, 3, 2) == 1:      ## orderType을 Sell & Buy(2) 로 변경
                                    if self.func_UPDATE_db_item(item_code, 4, sell_qty) == 1:    ## 복구를 위해 판매한 수량을 trAmount에 기입
                                        if MAKE_ORDER == 1:
                                            self.func_ORDER_SELL_auto(item_code, sell_qty, price)
                        
                        # Full Sell
                        if percent > 2 and step == STEP_LIMIT :
                            timestamp = self.func_GET_CurrentTime()
                            self.text_edit.append(timestamp + " " + item_code + " JUDGE : FULL 매도")
                            sell_qty = owncount
                            price = int(price_sell)

                            if self.func_UPDATE_db_item(item_code, 2, 1) == 1:      ## ordered 변경 -> 1
                                if self.func_UPDATE_db_item(item_code, 3, 3) == 1:  ## orderType 변경 -> 3
                                    if MAKE_ORDER == 1:
                                        self.func_ORDER_SELL_auto(item_code, sell_qty, price)

                        # STAY
                        if percent < -2 and step == STEP_LIMIT :
                            cur_time = time.time()
                            stay_time = int(self.stay_print_time[item_code])

                            if stay_time == 0 :
                                timestamp = self.func_GET_CurrentTime()
                                self.text_edit.append(timestamp + " " + item_code + " JUDGE : STAY")
                                self.stay_print_time[item_code] = int(cur_time)
                            else :
                                dur = int(cur_time - stay_time)
                                if dur > 60 :
                                    timestamp = self.func_GET_CurrentTime()
                                    self.text_edit.append(timestamp + " " + item_code + " JUDGE : STAY")
                                    self.stay_print_time[item_code] = int(cur_time)

                        else :
                            cur_time = time.time()
                            status_time = int(self.status_print_time[item_code])

                            if status_time == 0 :
                                timestamp = self.func_GET_CurrentTime()
                                self.text_edit.append(timestamp + " " + item_code + " JUDGE : STAY")
                                self.status_print_time[item_code] = int(cur_time)
                            else :
                                dur = int(cur_time - status_time)
                                if dur > 60 :
                                    timestamp = self.func_GET_CurrentTime()
                                    self.text_edit.append(timestamp + " " + item_code + " JUDGE : STAY")
                                    self.status_print_time[item_code] = int(cur_time)



if __name__=="__main__":
    app = QApplication(sys.argv)
    app.setStyle(QStyleFactory.create('Fusion')) # --> 없으면, 헤더색 변경 안됨.
    # print(sys.argv)
    myWindow = Kiwoom()
    myWindow.show()
    app.exec_()