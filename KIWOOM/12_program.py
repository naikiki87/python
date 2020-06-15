import sys
import time
from time import localtime, strftime
import pandas as pd

from PyQt5.QtWidgets import *
from PyQt5.QAxContainer import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5 import QtTest, QtCore, QtWidgets, uic
import module_timer
import module_get_summary
import module_item_finder

form_class = uic.loadUiType("interface.ui")[0]

for i in range(10) :
    globals()['DF_item{}'.format(i)] = pd.DataFrame(columns = ['code', '%', 'm_1', 'm_2', 'm_3', 'm_4', 'm_5', 'm_6', 'm_7', 'm_8', 'm_9', 'm_10'])
    globals()['save_times{}'.format(i)] = 0
    globals()['elapsed_min{}'.format(i)] = 0

# self.df_history = pd.DataFrame(columns = ['day', 'type', 'T_ID', 'time', 'Code', 'Name', 'Qty', 'Price', 'Req_ID'])

class Kiwoom(QMainWindow, form_class):
    index = 0
    time = 0
    flag_cont_CheckBalance = 0
    init_history = 0
    flag_HistoryData_Auto = 0
    flag_ItemInfo_click = 0
    auto_buy = 0
    # self.df_history = pd.DataFrame(columns = ['day', 'type', 'T_ID', 'time', 'Code', 'Name', 'Qty', 'Price', 'Req_ID'])
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.kiwoom = QAxWidget()
        self.kiwoom.setControl("KHOPENAPI.KHOpenAPICtrl.1")

        self.comm_connect()       # Aloha
        
        self.kiwoom.OnEventConnect.connect(self.event_connect)
        self.kiwoom.OnReceiveTrData.connect(self.receive_tr_data)
        self.kiwoom.OnReceiveChejanData.connect(self.receive_chejan_data)

        self.init_UI()

    def init_UI(self) :
        self.cnt_tab_history = 0

        self.btn0.clicked.connect(self.func_GET_ItemInfo)
        self.btn2.clicked.connect(self.btn_buy_order)
        self.btn3.clicked.connect(self.btn_sell_order)
        self.btn4.clicked.connect(self.btn_test)
        self.btn5.clicked.connect(self.func_START_CheckBalance)
        self.btn6.clicked.connect(self.func_STOP_CheckBalance)
        self.btn7.clicked.connect(self.func_GET_TradeHistory)

        self.func_SET_tableSUMMARY()
        self.func_SET_tableHISTORY()

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

    def receive_tr_data(self, screen_no, rqname, trcode, recordname, prev_next, data_len, err_code, msg1, msg2):
        print("data received")
        if next == '2':
            self.remained_data = True
        else:
            self.remained_data = False

        if rqname == "GET_ItemInfo":
            self.func_SHOW_ItemInfo(rqname, trcode, recordname)

        if rqname == "opw00018_req":
            self.show_opw00018(rqname, trcode, recordname)

        if rqname == "opw00009_man":
            print("opw20009 man")
            self.func_SHOW_TradeHistory(rqname, trcode, recordname)

        if rqname == "opw00009_req":
            if self.init_history == 1:
                self.init_history_table(rqname, trcode, recordname)
            else :
                print("#######")
                # self.func_SHOW_TradeHistory(rqname, trcode, recordname)


            self.show_opt10004(rqname, trcode, recordname)

    def func_GET_TradeHistory(self, date) :       # search history data manually
        self.df_history = pd.DataFrame(columns = ['day', 'time', 'type', 'T_ID', 'Code', 'Name', 'Qty', 'Price', 'Req_ID'])

        if self.flag_HistoryData_Auto == 1:
            self.search_date = date
            self.flag_HistoryData_Auto = 0
        else :
            self.search_date = self.input_history_date.text()

        print("Date : ", self.search_date)

        acc_no = "8137639811"
        acc_pw = "6458"
        self.kiwoom.dynamicCall("SetInputValue(QString, QString)", "주문일자", self.search_date)
        self.kiwoom.dynamicCall("SetInputValue(QString, QString)", "계좌번호", "8137639811")
        self.kiwoom.dynamicCall("SetInputValue(QString, QString)", "비밀번호", "6458")
        self.kiwoom.dynamicCall("SetInputValue(QString, QString)", "비밀번호입력매체구분", "00")
        self.kiwoom.dynamicCall("SetInputValue(QString, QString)", "주식채권구분", "0")
        self.kiwoom.dynamicCall("CommRqData(QString, QString, int, QString)", "opw00009_man", "opw00009", 0, "0101")

    def btn_test(self) :                # search histlry data automatically
        self.search_date_list = list(range(20200601, 20200612))
        self.search_date_list = list(map(str, self.search_date_list))
        self.history_index = 0
        self.init_history = 1
        self.cnt_check_history = 0
        self.cnt_tab_history = 0

        self.df_history = pd.DataFrame(columns = ['day', 'type', 'T_ID', 'time', 'Code', 'Name', 'Qty', 'Price', 'Req_ID'])

        self.get_trade_history2()

    def get_trade_history2(self):
        self.search_date = self.search_date_list[self.history_index]
        # print("Src Date : ", self.search_date)
        acc_no = "8137639811"
        acc_pw = "6458"

        self.kiwoom.dynamicCall("SetInputValue(QString, QString)", "주문일자", self.search_date)
        self.kiwoom.dynamicCall("SetInputValue(QString, QString)", "계좌번호", "8137639811")
        self.kiwoom.dynamicCall("SetInputValue(QString, QString)", "비밀번호", "6458")
        self.kiwoom.dynamicCall("SetInputValue(QString, QString)", "비밀번호입력매체구분", "00")
        self.kiwoom.dynamicCall("SetInputValue(QString, QString)", "주식채권구분", "0")
        self.kiwoom.dynamicCall("CommRqData(QString, QString, int, QString)", "opw00009_req", "opw00009", 0, "0101")

    def init_history_table(self, rqname, trcode, recordname) :
        len_list = len(self.search_date_list)
        data_cnt = self.kiwoom.dynamicCall("GetCommData(QString, QString, int, QString)", trcode, recordname, 0, "조회건수")

        if data_cnt == "":
            print("nothing")
        
        else :
            data_cnt = int(data_cnt)

            for i in range(data_cnt):
                deal_type = self.kiwoom.dynamicCall("GetCommData(QString, QString, int, QString)", trcode, recordname, i, "주문유형구분")
                trade_no = self.kiwoom.dynamicCall("GetCommData(QString, QString, int, QString)", trcode, recordname, i, "체결번호")
                trade_time = self.kiwoom.dynamicCall("GetCommData(QString, QString, int, QString)", trcode, recordname, i, "체결시간")
                itemcode = self.kiwoom.dynamicCall("GetCommData(QString, QString, int, QString)", trcode, recordname, i, "종목번호")
                itemname = self.kiwoom.dynamicCall("GetCommData(QString, QString, int, QString)", trcode, recordname, i, "종목명")
                trade_amount = self.kiwoom.dynamicCall("GetCommData(QString, QString, int, QString)", trcode, recordname, i, "체결수량")
                trade_unit_price = self.kiwoom.dynamicCall("GetCommData(QString, QString, int, QString)", trcode, recordname, i, "체결단가")
                req_no = self.kiwoom.dynamicCall("GetCommData(QString, QString, int, QString)", trcode, recordname, i, "주문번호")

                self.df_history.loc[self.cnt_tab_history] = [self.search_date, deal_type, trade_no, trade_time, itemcode, itemname, int(trade_amount), round(float(trade_unit_price), 1), req_no]
                self.cnt_tab_history = self.cnt_tab_history + 1

        self.cnt_check_history = self.cnt_check_history + 1

        if self.cnt_check_history == len_list :
            self.init_history = 0
            self.df_history = self.df_history.sort_values(['day', 'time'], ascending=[False, False])
            self.df_history = self.df_history.reset_index(drop=True, inplace=False)

            data_cnt = len(self.df_history)

            for i in range(data_cnt):
                T_day = self.df_history.day[i]
                T_type = self.df_history.type[i]
                T_id = self.df_history.T_ID[i]
                T_time = self.df_history.time[i]
                T_code = self.df_history.Code[i]
                T_name = self.df_history.Name[i]
                T_qty = str(self.df_history.Qty[i])
                T_price = str(self.df_history.Price[i])
                T_reqid = str(self.df_history.Req_ID[i])

                self.func_SET_TableData(2, i, 0, T_day)
                self.func_SET_TableData(2, i, 1, T_type)
                self.func_SET_TableData(2, i, 2, T_id)
                self.func_SET_TableData(2, i, 3, T_time)
                self.func_SET_TableData(2, i, 4, T_code)
                self.func_SET_TableData(2, i, 5, T_name)
                self.func_SET_TableData(2, i, 6, T_qty)
                self.func_SET_TableData(2, i, 7, T_price)
                self.func_SET_TableData(2, i, 8, T_reqid)
            
            
        else :
            QtTest.QTest.qWait(280)
            self.history_index = self.history_index + 1
            self.get_trade_history2()

    def func_SHOW_TradeHistory(self, rqname, trcode, recordname):
        data_cnt = self.kiwoom.dynamicCall("GetCommData(QString, QString, int, QString)", trcode, recordname, 0, "조회건수")

        if data_cnt == "":
            self.table_history.clearContents()
            self.table_history.setRowCount(0)
        else :
            data_cnt = int(data_cnt)
            self.table_history.clearContents()
            self.table_history.setRowCount(data_cnt)

            for i in range(data_cnt) :
                deal_type = self.kiwoom.dynamicCall("GetCommData(QString, QString, int, QString)", trcode, recordname, i, "주문유형구분")
                trade_no = self.kiwoom.dynamicCall("GetCommData(QString, QString, int, QString)", trcode, recordname, i, "체결번호")
                trade_time = self.kiwoom.dynamicCall("GetCommData(QString, QString, int, QString)", trcode, recordname, i, "체결시간")
                itemcode = self.kiwoom.dynamicCall("GetCommData(QString, QString, int, QString)", trcode, recordname, i, "종목번호")
                itemname = self.kiwoom.dynamicCall("GetCommData(QString, QString, int, QString)", trcode, recordname, i, "종목명")
                trade_amount = self.kiwoom.dynamicCall("GetCommData(QString, QString, int, QString)", trcode, recordname, i, "체결수량")
                trade_unit_price = self.kiwoom.dynamicCall("GetCommData(QString, QString, int, QString)", trcode, recordname, i, "체결단가")
                req_no = self.kiwoom.dynamicCall("GetCommData(QString, QString, int, QString)", trcode, recordname, i, "주문번호")

                self.df_history.loc[i] = [self.search_date, trade_time, deal_type, trade_no, itemcode, itemname, int(trade_amount), round(float(trade_unit_price), 1), req_no]

            self.df_history = self.df_history.sort_values(by=['time'], axis=0, ascending=False)
            self.df_history = self.df_history.reset_index(drop=True, inplace=False)
            print(self.df_history)

            data_cnt = len(self.df_history)

            for i in range(data_cnt):
                self.func_SET_TableData(2, i, 0, self.df_history.day[i])
                self.func_SET_TableData(2, i, 1, self.df_history.time[i])
                self.func_SET_TableData(2, i, 2, self.df_history.type[i])
                self.func_SET_TableData(2, i, 3, self.df_history.T_ID[i])
                self.func_SET_TableData(2, i, 4, self.df_history.Code[i])
                self.func_SET_TableData(2, i, 5, self.df_history.Name[i])
                self.func_SET_TableData(2, i, 6, str(self.df_history.Qty[i]))
                self.func_SET_TableData(2, i, 7, str(self.df_history.Price[i]))
                self.func_SET_TableData(2, i, 8, str(self.df_history.Req_ID[i]))
            
    def func_SET_TableData(self, table_no, row, col, content):
        if table_no == 1:
            item = QTableWidgetItem(content)
            item.setTextAlignment(QtCore.Qt.AlignVCenter | QtCore.Qt.AlignHCenter)
            self.table_summary.setItem(row, col, item)
        if table_no == 2:
            item = QTableWidgetItem(content)
            item.setTextAlignment(QtCore.Qt.AlignVCenter | QtCore.Qt.AlignHCenter)
            self.table_history.setItem(row, col, item)

    # def btn_test(self):
    #     self.item_finder = module_item_finder.Item_Finder()
    #     self.item_finder.item_finder_messages.connect(self.item_finder_messages)
    #     self.item_finder.item_finder_items.connect(self.item_finder_items)
    #     self.item_finder.start()
        # a = 0
        
    
    
    ## [START] login ##
    def comm_connect(self):
        self.kiwoom.dynamicCall("CommConnect()")
        self.login_event_loop = QThread()
        self.login_event_loop.start()


        # btn = QPushButton(self.table_history)
        # btn.setText('12/1/12')
        # self.table_history.setCellWidget(0, 0, btn)

    def event_connect(self, err_code):
        if err_code == 0:
            self.text_edit.append("CONNECTED")
            self.timer = module_timer.Timer()
            self.timer.cur_time.connect(self.update_times)
            
            # self.buy_test()
            self.timer.start()
            self.text_edit.append("timer thread started")
            self.login_event_loop.terminate()

            # self.func_START_CheckBalance()          # Aloha
            # self.btn_test()
            
        else:
            print("DISCONNECTED")
    ## [END] login ##

    def buy_test(self):
        cnt = 0
        for i in range(10) :
            # self.text_edit.append(str(cnt))
            cnt = cnt + 1
            QtTest.QTest.qWait(1000)

    ## 매수 ##
    def btn_buy_order(self) :
        self.text_edit.append("BUY Clicked")
        item_code = self.code_edit.text()
        qty = int(self.buy_sell_count.text())
        price = int(self.buy_price.text())

        self.buy_order(item_code, qty, price)

    def buy_order(self, item_code, qty, price) :
        self.text_edit.append("Send Order : BUY")
        rqname = "RQ_TEST"
        screen_no = "0101"
        acc_no = "8137639811"
        order_type = 1
        hogagb = "00"
        orgorderno = ""
        order = self.kiwoom.dynamicCall("SendOrder(QString, QString, QString, int, QString, int, int, QString, QString)",
                     [rqname, screen_no, acc_no, order_type, item_code, qty, price, hogagb, orgorderno])

    ## 매도 ##
    def btn_sell_order(self) :
        self.text_edit.append("SELL Clicked")
        item_code = self.code_edit.text()
        qty = int(self.buy_sell_count.text())
        price = int(self.buy_price.text())

        self.sell_order(item_code, qty, price)

    def sell_order(self, item_code, qty, price) :
        self.text_edit.append("Send Order : SELL")
        rqname = "RQ_TEST"
        screen_no = "0101"
        acc_no = "8137639811"
        order_type = 2
        hogagb = "00"
        orgorderno = ""
        
        order = self.kiwoom.dynamicCall("SendOrder(QString, QString, QString, int, QString, int, int, QString, QString)",
                     [rqname, screen_no, acc_no, order_type, item_code, qty, price, hogagb, orgorderno])
        
    def get_chejan_data(self, fid):
        ret = self.kiwoom.dynamicCall("GetChejanData(int)", fid)
        return ret
    def receive_chejan_data(self, gubun, item_cnt, fid_list):
        if gubun == "0" :
            self.text_edit3.append("-- 체결완료 --")
        self.text_edit3.append("주문번호 : " + self.get_chejan_data(9203))
        self.text_edit3.append("종목명 : " + self.get_chejan_data(302))
        self.text_edit3.append("체결가 : " + self.get_chejan_data(910))
        self.text_edit3.append("체결량 : " + self.get_chejan_data(911))
        self.text_edit3.append("체결단가 : " + self.get_chejan_data(931))
        self.text_edit3.append("")

        ##### 체결시 history table 갱신 수행
        year = strftime("%Y", localtime())
        month = strftime("%m", localtime())
        day = strftime("%d", localtime())
        today = year + month + day

        self.flag_HistoryData_Auto = 1
        self.func_GET_TradeHistory(today)

    def func_GET_ItemInfo(self, code):
        if self.flag_ItemInfo_click == 0:
            code = self.code_edit.text()
        else :
            code = code
            self.flag_ItemInfo_click = 0
        
        self.kiwoom.dynamicCall("SetInputValue(QString, QString)", "종목코드", code)
        self.kiwoom.dynamicCall("CommRqData(QString, QString, int, QString)", "GET_ItemInfo", "opt10001", 0, "0101")

    def get_order_price(self, item_code) :
        self.kiwoom.dynamicCall("SetInputValue(QString, QString)", "종목코드", item_code)
        self.kiwoom.dynamicCall("CommRqData(QString, QString, int, QString)", "opt10004_req", "opt10004", 0, "0101")

    def func_START_CheckBalance(self):
        # self.btn_test()       # start get history data automatically
        self.buy_cnt = 0
        self.auto_buy = 0
        self.request_times = 0
        acc_no = "8137639811"
        acc_pw = "6458"
        # acc_pw = self.input_acc_pw.text()
        if acc_pw != "6458":
            self.text_edit.append("Password Incorrect")
        else :
            self.flag_cont_CheckBalance = 1
            while self.flag_cont_CheckBalance:
                if self.buy_cnt == 2:
                    self.auto_buy = 1
                # self.text_edit.append(str(self.buy_cnt))
                # self.buy_cnt = self.buy_cnt + 1

                self.kiwoom.dynamicCall("SetInputValue(QString, QString)", "계좌번호", acc_no)
                self.kiwoom.dynamicCall("SetInputValue(QString, QString)", "비밀번호", acc_pw)
                self.kiwoom.dynamicCall("CommRqData(QString, QString, int, QString)", "opw00018_req", "opw00018", 0, "0101")
                QtTest.QTest.qWait(3000)

    def func_STOP_CheckBalance(self):
        self.flag_cont_CheckBalance = 0

    def show_opt10004(self, rqname, trcode, recordname):
        a= 0

    def func_SHOW_ItemInfo(self, rqname, trcode, recordname):
        itemcode = self.kiwoom.dynamicCall("GetCommData(QString, QString, int, QString)", trcode, recordname, 0, "종목코드")
        name = self.kiwoom.dynamicCall("GetCommData(QString, QString, int, QString)", trcode, recordname, 0, "종목명")
        volume = self.kiwoom.dynamicCall("GetCommData(QString, QString, int, QString)", trcode, recordname, 0, "거래량")
        numStocks = self.kiwoom.dynamicCall("GetCommData(QString, QString, int, QString)", trcode, recordname, 0, "상장주식")
        prices = self.kiwoom.dynamicCall("GetCommData(QString, QString, int, QString)", trcode, recordname, 0, "시가")
        percent = self.kiwoom.dynamicCall("GetCommData(QString, QString, int, QString)", trcode, recordname, 0, "등락율")
        per = self.kiwoom.dynamicCall("GetCommData(QString, QString, int, QString)", trcode, recordname, 0, "PER")
        current_price = self.kiwoom.dynamicCall("GetCommData(QString, QString, int, QString)", trcode, recordname, 0, "현재가")
        current_price = current_price.strip()
        current_price = int(current_price)

        if current_price < 0:        
            current_price = current_price * -1

        # self.text_edit.append("Request Item Info : " + itemcode.strip())
        # self.text_edit2.setText("종목코드:" + itemcode.strip())
        # self.text_edit2.append("종목명:" + name.strip())
        # self.text_edit2.append("거래량:" + volume.strip())
        # self.text_edit2.append("상장주식:" + numStocks.strip())
        # self.text_edit2.append("시가:" + prices.strip())
        # self.text_edit2.append("등락:" + percent.strip() + " %")
        # self.text_edit2.append("PER:" + per.strip())
        # self.text_edit2.append("현재가:" + str(current_price))

        self.te_iteminfo_code.setText(itemcode.strip())
        self.te_iteminfo_name.setText(name.strip())
        self.te_iteminfo_price.setText(str(current_price))
        self.te_iteminfo_vol.setText(volume.strip())
        self.te_iteminfo_percent.setText(percent.strip() + " %")

        if self.auto_buy == 1:
            self.text_edit.append("BUY")
            self.text_edit.append("종목 : " + name.strip())
            self.text_edit.append("현재가 : " + str(current_price))

            # self.buy_order(itemcode.strip(), 1, current_price + 50)                   ## auto buy
            self.auto_buy = 0
            

    def show_opw00018(self, rqname, trcode, recordname):
        data_cnt = self.get_repeat_cnt(trcode, rqname)

        total_purchase = self.kiwoom.dynamicCall("GetCommData(QString, QString, int, QString)", trcode, recordname, 0, "총매입금액")
        total_evaluation = self.kiwoom.dynamicCall("GetCommData(QString, QString, int, QString)", trcode, recordname, 0, "총평가금액")

        # self.text_edit5.setText(str(int(total_purchase)))
        # self.text_edit6.setText(str(int(total_evaluation)))
        self.wid_total_purchase.setText(str(int(total_purchase)))
        self.wid_total_evaluation.setText(str(int(total_evaluation)))

        for i in range(data_cnt) :
            total_percent = self.kiwoom.dynamicCall("GetCommData(QString, QString, int, QString)", trcode, recordname, i, "총수익률(%)")
            capital = self.kiwoom.dynamicCall("GetCommData(QString, QString, int, QString)", trcode, recordname, i, "추정예탁자산")
            itemcode = self.kiwoom.dynamicCall("GetCommData(QString, QString, int, QString)", trcode, recordname, i, "종목번호")
            itemname = self.kiwoom.dynamicCall("GetCommData(QString, QString, int, QString)", trcode, recordname, i, "종목명")
            each_percent = self.kiwoom.dynamicCall("GetCommData(QString, QString, int, QString)", trcode, recordname, i, "수익률(%)")
            cur_price = self.kiwoom.dynamicCall("GetCommData(QString, QString, int, QString)", trcode, recordname, i, "현재가")
            unit_price = self.kiwoom.dynamicCall("GetCommData(QString, QString, int, QString)", trcode, recordname, i, "매입가")
            total_purchase_price = self.kiwoom.dynamicCall("GetCommData(QString, QString, int, QString)", trcode, recordname, i, "매입금액")
            total_evaluation_price = self.kiwoom.dynamicCall("GetCommData(QString, QString, int, QString)", trcode, recordname, i, "평가금액")
            owncount = self.kiwoom.dynamicCall("GetCommData(QString, QString, int, QString)", trcode, recordname, i, "보유수량")
            added_fee = self.kiwoom.dynamicCall("GetCommData(QString, QString, int, QString)", trcode, recordname, i, "수수료합")
            tax = self.kiwoom.dynamicCall("GetCommData(QString, QString, int, QString)", trcode, recordname, i, "세금")
            eval_pl = self.kiwoom.dynamicCall("GetCommData(QString, QString, int, QString)", trcode, recordname, i, "평가손익")

            # print(globals()['save_times{}'.format(i)])

            if globals()['save_times{}'.format(i)] == 3:
                globals()['save_times{}'.format(i)] = 0
                m_1 = globals()['DF_item{}'.format(i)]['%'].mean()
                m_2 = globals()['DF_item{}'.format(i)].loc[0]['m_1']
                m_3 = globals()['DF_item{}'.format(i)].loc[0]['m_2']
                m_4 = globals()['DF_item{}'.format(i)].loc[0]['m_3']
                m_5 = globals()['DF_item{}'.format(i)].loc[0]['m_4']
                m_6 = globals()['DF_item{}'.format(i)].loc[0]['m_5']
                m_7 = globals()['DF_item{}'.format(i)].loc[0]['m_6']
                m_8 = globals()['DF_item{}'.format(i)].loc[0]['m_7']
                m_9 = globals()['DF_item{}'.format(i)].loc[0]['m_8']
                m_10 = globals()['DF_item{}'.format(i)].loc[0]['m_9']

                globals()['DF_item{}'.format(i)].loc[globals()['save_times{}'.format(i)]] = [itemcode, round(float(each_percent), 2), m_1, m_2, m_3, m_4, m_5, m_6, m_7, m_8, m_9, m_10]
                globals()['save_times{}'.format(i)] = globals()['save_times{}'.format(i)] + 1
            else:
                globals()['DF_item{}'.format(i)].loc[globals()['save_times{}'.format(i)]] = [itemcode, round(float(each_percent), 2), 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
                globals()['save_times{}'.format(i)] = globals()['save_times{}'.format(i)] + 1

            # '{0:,}'.format()
            # str('{0:,}'.format())
            # total_fee = int(float(added_fee) + float(tax))
            total_sum = str('{0:,}'.format(int(total_evaluation_price) - int(total_purchase_price)))
            owncount = str('{0:,}'.format(int(owncount)))
            cur_price = str('{0:,}'.format(int(cur_price)))
            unit_price = str('{0:,}'.format(int(unit_price)))
            total_evaluation_price = str('{0:,}'.format(int(total_evaluation_price)))
            total_purchase_price = str('{0:,}'.format(int(total_purchase_price)))
            total_fee = str('{0:,}'.format(int(float(added_fee) + float(tax))))
            eval_pl = str('{0:,}'.format(int(eval_pl)))

            self.func_SET_TableData(1, 2*i, 0, itemcode)
            self.func_SET_TableData(1, 2*i, 1, itemname)
            self.func_SET_TableData(1, 2*i, 2, owncount)
            self.func_SET_TableData(1, 2*i, 3, cur_price)
            self.func_SET_TableData(1, (2*i + 1), 3, unit_price)
            self.func_SET_TableData(1, 2*i, 4, total_evaluation_price)
            self.func_SET_TableData(1, (2*i + 1), 4, total_purchase_price)
            self.func_SET_TableData(1, 2*i, 5, total_sum)
            self.func_SET_TableData(1, 2*i, 6, total_fee)
            self.func_SET_TableData(1, 2*i, 7, eval_pl)
            self.func_SET_TableData(1, 2*i, 8, str(round(float(each_percent), 2)))

        self.wid_req_times.setText(str(self.request_times))
        self.request_times = self.request_times + 1
        # print(DF_item0)

    def get_repeat_cnt(self, trcode, rqname):
        ret = self.kiwoom.dynamicCall("GetRepeatCnt(QString, QString)", trcode, rqname)
        return ret

    def func_SET_tableSUMMARY(self):
        row_count = 10
        col_count = 9
        # self.table_summary.resize(592, 211)
        
        # self.table_summary.move(430, 130)
        self.table_summary.setRowCount(row_count)
        self.table_summary.setColumnCount(col_count)
        self.table_summary.resizeRowsToContents()
        # self.table_summary.resizeColumnsToContents()

        for i in range(col_count):
            self.table_summary.setColumnWidth(i, 70)
        self.table_summary.setColumnWidth(2, 50)
        self.table_summary.setColumnWidth(8, 50)
        self.table_summary.verticalHeader().setVisible(False)
        self.table_summary.verticalHeader().setDefaultSectionSize(1)

        for i in range(int(row_count/2)):
            j=i*2
            self.table_summary.setSpan(j,0,2,1)
            self.table_summary.setSpan(j,1,2,1)
            self.table_summary.setSpan(j,2,2,1)
            self.table_summary.setSpan(j,5,2,1)
            self.table_summary.setSpan(j,6,2,1)
            self.table_summary.setSpan(j,7,2,1)
            self.table_summary.setSpan(j,8,2,1)
        
        self.table_summary.setHorizontalHeaderItem(0, QTableWidgetItem("Code"))
        self.table_summary.setHorizontalHeaderItem(1, QTableWidgetItem("종목"))
        self.table_summary.setHorizontalHeaderItem(2, QTableWidgetItem("수량"))
        self.table_summary.setHorizontalHeaderItem(3, QTableWidgetItem("단가"))
        self.table_summary.setHorizontalHeaderItem(4, QTableWidgetItem("금액"))
        self.table_summary.setHorizontalHeaderItem(5, QTableWidgetItem("합계"))
        self.table_summary.setHorizontalHeaderItem(6, QTableWidgetItem("수수료"))
        self.table_summary.setHorizontalHeaderItem(7, QTableWidgetItem("손익"))
        self.table_summary.setHorizontalHeaderItem(8, QTableWidgetItem("%"))

        self.table_summary.clicked.connect(self.func_GET_ItemInfo_by_click)

    def func_SET_tableHISTORY(self):
        row_count = 0
        col_count = 9
        # self.table_history.resize(722, 250)
        
        self.table_history.setRowCount(row_count)
        self.table_history.setColumnCount(col_count)
        self.table_history.resizeRowsToContents()
        # self.table_history.resizeColumnsToContents()

        for i in range(col_count):
            self.table_history.setColumnWidth(i, 80)
        self.table_history.verticalHeader().setVisible(False)
        self.table_history.verticalHeader().setDefaultSectionSize(1)

        # header_item = QTableWidgetItem("추가") 
        # header_item.setBackground(Qt.red) # 헤더 배경색 설정 --> app.setStyle() 설정해야만 작동한다. 
        # self.table_history.setHorizontalHeaderItem(0, header_item)

        self.table_history.setHorizontalHeaderItem(0, QTableWidgetItem("날짜"))
        self.table_history.setHorizontalHeaderItem(1, QTableWidgetItem("체결시간"))
        self.table_history.setHorizontalHeaderItem(2, QTableWidgetItem("구분"))
        self.table_history.setHorizontalHeaderItem(3, QTableWidgetItem("체결번호"))
        self.table_history.setHorizontalHeaderItem(4, QTableWidgetItem("종목번호"))
        self.table_history.setHorizontalHeaderItem(5, QTableWidgetItem("종 목 명"))
        self.table_history.setHorizontalHeaderItem(6, QTableWidgetItem("체결수량"))
        self.table_history.setHorizontalHeaderItem(7, QTableWidgetItem("체결단가"))
        self.table_history.setHorizontalHeaderItem(8, QTableWidgetItem("주문번호"))
    
    def func_GET_ItemInfo_by_click(self, index) :
        row = index.row()
        if row % 2 == 1:
            row = row - 1
        itemcode = self.table_summary.item(row, 0).text()
        itemcode = itemcode.replace("A", "")
        self.flag_ItemInfo_click = 1
        self.func_GET_ItemInfo(itemcode.strip())

if __name__=="__main__":
    app = QApplication(sys.argv)
    app.setStyle(QStyleFactory.create('Fusion')) # --> 없으면, 헤더색 변경 안됨.
    # print(sys.argv)
    myWindow = Kiwoom()
    myWindow.show()
    app.exec_()