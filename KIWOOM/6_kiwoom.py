import sys
import time
import pandas as pd

from PyQt5.QtWidgets import *
from PyQt5.QAxContainer import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5 import QtTest, QtCore, QtWidgets
import module_timer
import module_worker


class Kiwoom(QMainWindow):
    index = 0
    time = 0
    is_continue = 0
    def __init__(self):
        super().__init__()
        self.kiwoom = QAxWidget()
        self.kiwoom.setControl("KHOPENAPI.KHOpenAPICtrl.1")


        self.comm_connect()       # Aloha


        self.kiwoom.OnEventConnect.connect(self.event_connect)
        self.kiwoom.OnReceiveTrData.connect(self.receive_tr_data)
        self.kiwoom.OnReceiveChejanData.connect(self.receive_chejan_data)

        self.init_UI()

    @pyqtSlot(str)
    def update_times(self, data) :
        self.text_edit4.setText(data)

    @pyqtSlot(dict)
    def update_times2(self, data) :
        price = data[(0, "cur_price")]
        self.setTableWidgetData(1,0,0,str(price))


    def init_UI(self) :
        self.setWindowTitle("AutoK")
        self.setGeometry(100, 100, 1700, 600)

        label = QLabel('종목코드', self)
        label.move(20, 10)
        self.code_edit = QLineEdit(self)
        self.code_edit.move(80, 10)

        label = QLabel('금액', self)
        label.move(20, 50)
        self.buy_price = QLineEdit(self)
        self.buy_price.move(80, 50)

        btn0 = QPushButton('조회', self)
        btn0.move(190, 10)
        btn0.clicked.connect(self.btn_item_info)

        btn2 = QPushButton('매수주문', self)
        btn2.move(190, 90)
        btn2.clicked.connect(self.btn_buy_order)

        btn3 = QPushButton('매도주문', self)
        btn3.move(290, 90)
        btn3.clicked.connect(self.btn_sell_order)
        
        btn4 = QPushButton('TES2T', self)
        btn4.move(290, 140)
        btn4.clicked.connect(self.btn_test)

        # btn4 = QPushButton('TES2Tddd', self)
        # btn4.move(190, 140)
        # btn4.clicked.connect(self.btn_test2)

        label = QLabel('수량', self)
        label.move(20, 90)
        self.buy_sell_count = QLineEdit(self)
        self.buy_sell_count.move(80, 90)

        label = QLabel('비밀번호', self)
        label.move(430, 10)
        self.input_acc_pw = QLineEdit(self)
        self.input_acc_pw.setEchoMode(QLineEdit.Password)
        self.input_acc_pw.move(500, 10)

        btn5 = QPushButton('실행', self)
        btn5.move(630, 10)
        btn5.clicked.connect(self.check_balance)

        btn6 = QPushButton('중지', self)
        btn6.move(730, 10)
        btn6.clicked.connect(self.stop_check_balance)

        self.table_summary = QTableWidget(self)   # 보유내역 table
        self.set_table_summary()

        label = QLabel('매매일자', self)
        label.move(1100, 10)
        self.input_history_date = QLineEdit(self)
        self.input_history_date.move(1180, 10)

        btn7 = QPushButton('검색', self)
        btn7.move(1300, 10)
        btn7.clicked.connect(self.get_trade_history)

        self.table_history = QTableWidget(self)     # 매매 history
        self.set_table_history()

        self.text_edit = QTextEdit(self)
        self.text_edit.setGeometry(10, 180, 190, 150)
        self.text_edit.setEnabled(False)    # 텍스트창의 내용물 활용여부 (False : 읽기모드)

        self.text_edit2 = QTextEdit(self)
        self.text_edit2.setGeometry(210, 180, 200, 150)
        self.text_edit2.setEnabled(False)
        
        self.text_edit3 = QTextEdit(self)
        self.text_edit3.setGeometry(10, 340, 400, 150)
        self.text_edit3.setEnabled(False)

        self.text_edit4 = QTextEdit(self)
        self.text_edit4.setGeometry(870, 15, 80, 30)
        self.text_edit4.setEnabled(False)
        self.text_edit4.setStyleSheet("border-style : none;")

        # 총매입금액 표시
        label = QLabel('총매입금액', self)
        label.move(750, 50)
        self.text_edit5 = QTextEdit(self)
        self.text_edit5.setGeometry(830, 50, 80, 30)
        self.text_edit5.setEnabled(False)

        # 총평가금액 표시
        label = QLabel('총평가금액', self)
        label.move(750, 90)
        self.text_edit6 = QTextEdit(self)
        self.text_edit6.setGeometry(830, 90, 80, 30)
        self.text_edit6.setEnabled(False)

    def btn_test(self) :
        # a = 10
        ## Back Worker -> import module_worker ##
        self.worker = module_worker.Worker()
        self.worker.finished2.connect(self.update_times2)
        self.worker.start()
        self.text_edit.append("worker thread started")

    def set_table_summary(self):
        row_count = 10
        col_count = 9
        self.table_summary.resize(592, 350)
        
        self.table_summary.move(430, 130)
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
        self.table_summary.setHorizontalHeaderItem(1, QTableWidgetItem("Name"))
        self.table_summary.setHorizontalHeaderItem(2, QTableWidgetItem("Count"))
        self.table_summary.setHorizontalHeaderItem(3, QTableWidgetItem("Unit Price"))
        
        self.table_summary.setHorizontalHeaderItem(4, QTableWidgetItem("Total Price"))
        
        self.table_summary.setHorizontalHeaderItem(5, QTableWidgetItem("sum"))
        self.table_summary.setHorizontalHeaderItem(6, QTableWidgetItem("fee"))
        self.table_summary.setHorizontalHeaderItem(7, QTableWidgetItem("평가손익"))
        self.table_summary.setHorizontalHeaderItem(8, QTableWidgetItem("%"))
    def set_table_history(self):
        row_count = 20
        col_count = 7
        self.table_history.resize(600, 480)
        
        self.table_history.move(1050, 50)
        self.table_history.setRowCount(row_count)
        self.table_history.setColumnCount(col_count)
        self.table_history.resizeRowsToContents()
        # self.table_history.resizeColumnsToContents()

        for i in range(col_count):
            self.table_history.setColumnWidth(i, 80)
        self.table_history.verticalHeader().setVisible(False)
        self.table_history.verticalHeader().setDefaultSectionSize(1)

        self.table_history.setHorizontalHeaderItem(0, QTableWidgetItem("체결번호"))
        self.table_history.setHorizontalHeaderItem(1, QTableWidgetItem("체결시간"))
        self.table_history.setHorizontalHeaderItem(2, QTableWidgetItem("종목번호"))
        self.table_history.setHorizontalHeaderItem(3, QTableWidgetItem("종 목 명"))
        self.table_history.setHorizontalHeaderItem(4, QTableWidgetItem("체결수량"))
        self.table_history.setHorizontalHeaderItem(5, QTableWidgetItem("체결단가"))
        self.table_history.setHorizontalHeaderItem(6, QTableWidgetItem("주문번호"))
    def test2(self):
        self.i = 1
    def setTableWidgetData(self, table_no, row, col, content):
        if table_no == 1:
            item = QTableWidgetItem(content)
            item.setTextAlignment(QtCore.Qt.AlignVCenter | QtCore.Qt.AlignHCenter)
            self.table_summary.setItem(row, col, item)
        if table_no == 2:
            item = QTableWidgetItem(content)
            item.setTextAlignment(QtCore.Qt.AlignVCenter | QtCore.Qt.AlignHCenter)
            self.table_history.setItem(row, col, item)
    ## [START] login ##
    def comm_connect(self):
        self.kiwoom.dynamicCall("CommConnect()")
        self.login_event_loop = QThread()
        self.login_event_loop.start()
    def event_connect(self, err_code):
        if err_code == 0:
            self.text_edit.append("CONNECTED")
            self.timer = module_timer.Timer()
            self.timer.cur_time.connect(self.update_times)
            self.timer.start()
            self.text_edit.append("timer thread started")
            self.login_event_loop.terminate()
        else:
            print("DISCONNECTED")
    ## [END] login ##

    ## 매수 ##
    def btn_buy_order(self):
        self.text_edit.append("Send Order : BUY")
        rqname = "RQ_TEST"
        screen_no = "0101"
        acc_no = "8137639811"
        order_type = 1
        item_code = self.code_edit.text()
        qty = int(self.buy_sell_count.text())
        price = int(self.buy_price.text())
        hogagb = "00"
        orgorderno = ""
        
        order = self.kiwoom.dynamicCall("SendOrder(QString, QString, QString, int, QString, int, int, QString, QString)",
                     [rqname, screen_no, acc_no, order_type, item_code, qty, price, hogagb, orgorderno])
    ## 매도 ##
    def btn_sell_order(self):
        self.text_edit.append("Send Order : SELL")
        rqname = "RQ_TEST"
        screen_no = "0101"
        acc_no = "8137639811"
        order_type = 2
        item_code = self.code_edit.text()
        qty = int(self.buy_sell_count.text())
        price = int(self.buy_price.text())
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

    def btn_item_info(self):
        code = self.code_edit.text()
        
        self.kiwoom.dynamicCall("SetInputValue(QString, QString)", "종목코드", code)
        self.kiwoom.dynamicCall("CommRqData(QString, QString, int, QString)", "opt10001_req", "opt10001", 0, "0101")

    def get_trade_history(self):
        # date = int(self.input_history_date.text())
        # date = self.input_history_date.text()
        # print(date)
        search_date = "20200603"
        acc_no = "8137639811"
        # acc_pw = "6458"
        acc_pw = self.input_acc_pw.text()
        if acc_pw != "6458" :
            self.text_edit.append("Wrong Password")
        else :

            self.kiwoom.dynamicCall("SetInputValue(QString, QString)", "주문일자", search_date)
            self.kiwoom.dynamicCall("SetInputValue(QString, QString)", "계좌번호", acc_no)
            self.kiwoom.dynamicCall("SetInputValue(QString, QString)", "비밀번호", acc_pw)
            # self.kiwoom.dynamicCall("SetInputValue(QString, QString)", "조회구분", 4)
            self.kiwoom.dynamicCall("CommRqData(QString, QString, int, QString)", "opw00009_req", "opw00009", 0, "0101")
            # self.kiwoom.dynamicCall("CommRqData(QString, QString, int, QString)", "OPW00007_req", "OPW00007", 0, "0101")

    def iterative_test(self) :
        i = 0
        while i <= 5 :
            self.check_balance()
            i = i + 1
            QtTest.QTest.qWait(1000)
    
    def check_balance(self):
        acc_no = "8137639811"
        acc_pw = self.input_acc_pw.text()
        if acc_pw != "6458":
            self.text_edit.append("Password Incorrect")
        else :
            self.is_continue = 1
            while self.is_continue:
                self.kiwoom.dynamicCall("SetInputValue(QString, QString)", "계좌번호", acc_no)
                self.kiwoom.dynamicCall("SetInputValue(QString, QString)", "비밀번호", acc_pw)
                self.kiwoom.dynamicCall("CommRqData(QString, QString, int, QString)", "opw00018_req", "opw00018", 0, "0101")
                QtTest.QTest.qWait(3000)

    def stop_check_balance(self):
        self.is_continue = 0

    def receive_tr_data(self, screen_no, rqname, trcode, recordname, prev_next, data_len, err_code, msg1, msg2):
        print("data received.")

        print("rqname", rqname)
        print("trcode", trcode)
        print("recordname", recordname)

        if next == '2':
            self.remained_data = True
        else:
            self.remained_data = False

        if rqname == "opt10001_req":
            self.show_opt10001(rqname, trcode, recordname)

        if rqname == "opw00018_req":
            self.show_opw00018(rqname, trcode, recordname)

        if rqname == "opw00009_req":
            print("HERE")
            ret = self.kiwoom.dynamicCall("GetRepeatCnt(QString, QString)", trcode, rqname)
            print(ret)
            self.show_opw00009(rqname, trcode, recordname)
        if rqname == "OPW00007_req":
            # print("HERER")
            # print(err_code)
            # data_cnt = self.get_repeat_cnt(trcode, recordname)
            # print(data_cnt)
            self.show_OPW00007(rqname, trcode, recordname)

    def show_opt10001(self, rqname, trcode, recordname):
        itemcode = self.kiwoom.dynamicCall("GetCommData(QString, QString, int, QString)", trcode, recordname, 0, "종목코드")
        name = self.kiwoom.dynamicCall("GetCommData(QString, QString, int, QString)", trcode, recordname, 0, "종목명")
        volume = self.kiwoom.dynamicCall("GetCommData(QString, QString, int, QString)", trcode, recordname, 0, "거래량")
        numStocks = self.kiwoom.dynamicCall("GetCommData(QString, QString, int, QString)", trcode, recordname, 0, "상장주식")
        prices = self.kiwoom.dynamicCall("GetCommData(QString, QString, int, QString)", trcode, recordname, 0, "시가")
        per = self.kiwoom.dynamicCall("GetCommData(QString, QString, int, QString)", trcode, recordname, 0, "PER")
        current_price = self.kiwoom.dynamicCall("GetCommData(QString, QString, int, QString)", trcode, recordname, 0, "현재가")
        current_price = current_price.strip()
        current_price = int(current_price)
        if current_price < 0:        
            current_price = current_price * -1

        self.text_edit.append("Request Item Info : " + itemcode.strip())

        self.text_edit2.setText("종목코드:" + itemcode.strip())
        self.text_edit2.append("종목명:" + name.strip())
        self.text_edit2.append("거래량:" + volume.strip())
        self.text_edit2.append("상장주식:" + numStocks.strip())
        self.text_edit2.append("시가:" + prices.strip())
        self.text_edit2.append("PER:" + per.strip())
        self.text_edit2.append("현재가:" + str(current_price))

    def show_opw00018(self, rqname, trcode, recordname):
        data_cnt = self.get_repeat_cnt(trcode, rqname)

        total_purchase = self.kiwoom.dynamicCall("GetCommData(QString, QString, int, QString)", trcode, recordname, 0, "총매입금액")
        total_evaluation = self.kiwoom.dynamicCall("GetCommData(QString, QString, int, QString)", trcode, recordname, 0, "총평가금액")

        self.text_edit5.setText(str(int(total_purchase)))
        self.text_edit6.setText(str(int(total_evaluation)))

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

            # print("total_fee : ", total_fee)

            self.setTableWidgetData(1, 2*i, 0, itemcode)
            self.setTableWidgetData(1, 2*i, 1, itemname)
            self.setTableWidgetData(1, 2*i, 2, owncount)
            # self.setTableWidgetData(1, 2*i, 2, str(int(owncount)))
            # self.setTableWidgetData(1, 2*i, 2, str(int('{0:,}'.format(owncount))))

            # self.setTableWidgetData(1, 2*i, 3, str(int(cur_price)))
            # self.setTableWidgetData(1, (2*i + 1), 3, str(int(unit_price)))
            self.setTableWidgetData(1, 2*i, 3, cur_price)
            self.setTableWidgetData(1, (2*i + 1), 3, unit_price)
            
            # self.setTableWidgetData(1, (2*i + 1), 3, str(int('{0:,}'.format(unit_price))))
            
            # self.setTableWidgetData(1, 2*i, 4, str(int(total_evaluation_price)))
            # self.setTableWidgetData(1, (2*i + 1), 4, str(int(total_purchase_price)))
            self.setTableWidgetData(1, 2*i, 4, total_evaluation_price)
            self.setTableWidgetData(1, (2*i + 1), 4, total_purchase_price)

            
            # self.setTableWidgetData(1, 2*i, 6, str(total_fee))
            self.setTableWidgetData(1, 2*i, 5, total_sum)
            self.setTableWidgetData(1, 2*i, 6, total_fee)
            
            self.setTableWidgetData(1, 2*i, 7, eval_pl)
            self.setTableWidgetData(1, 2*i, 8, str(round(float(each_percent), 2)))

    def show_opw00009(self, rqname, trcode, recordname):
        print("Show opw00009")
        # data_cnt = self.kiwoom.dynamicCall("GetCommData(QString, QString, int, QString)", trcode, recordname, 0, "조회건수")
        
        data_cnt = self.get_repeat_cnt(trcode, rqname)
        print("count : ", data_cnt)

        # for i in range(data_cnt) :

        #     trade_no = self.kiwoom.dynamicCall("GetCommData(QString, QString, int, QString)", trcode, recordname, i, "체결번호")
        #     trade_time = self.kiwoom.dynamicCall("GetCommData(QString, QString, int, QString)", trcode, recordname, i, "체결시간")
        #     itemcode = self.kiwoom.dynamicCall("GetCommData(QString, QString, int, QString)", trcode, recordname, i, "종목번호")
        #     itemname = self.kiwoom.dynamicCall("GetCommData(QString, QString, int, QString)", trcode, recordname, i, "종목명")
        #     trade_amount = self.kiwoom.dynamicCall("GetCommData(QString, QString, int, QString)", trcode, recordname, i, "체결수량")
        #     trade_unit_price = self.kiwoom.dynamicCall("GetCommData(QString, QString, int, QString)", trcode, recordname, i, "체결단가")
        #     req_no = self.kiwoom.dynamicCall("GetCommData(QString, QString, int, QString)", trcode, recordname, i, "주문번호")

        #     self.setTableWidgetData(2, i, 0, trade_no)
        #     self.setTableWidgetData(2, i, 1, trade_time)
        #     self.setTableWidgetData(2, i, 2, itemcode)
        #     self.setTableWidgetData(2, i, 3, itemname)
        #     self.setTableWidgetData(2, i, 4, trade_amount)
        #     self.setTableWidgetData(2, i, 5, trade_unit_price)
        #     self.setTableWidgetData(2, i, 6, req_no)

    def show_OPW00007(self, rqname, trcode, recordname):
        print("Show OPW00007")
        data_cnt = self.kiwoom.dynamicCall("GetCommData(QString, QString, int, QString)", trcode, recordname, 0, "출력건수")
        # data_cnt = self.get_repeat_cnt(trcode, rqname)
        # print(int(data_cnt))
        print("출력건수", data_cnt)

    def get_repeat_cnt(self, trcode, rqname):
        ret = self.kiwoom.dynamicCall("GetRepeatCnt(QString, QString)", trcode, rqname)
        return ret

if __name__=="__main__":
    app = QApplication(sys.argv)
    print(sys.argv)
    myWindow = Kiwoom()
    myWindow.show()
    app.exec_()