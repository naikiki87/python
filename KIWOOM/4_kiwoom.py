import sys
import time
import pandas as pd

from PyQt5.QtWidgets import *
from PyQt5.QAxContainer import *
from PyQt5.QtGui import *
# from PyQt5.QtCore import QThread, QObject, pyqtSignal
from PyQt5.QtCore import *
from PyQt5 import QtTest, QtCore

class Timer(QThread):
    finished = pyqtSignal(int)

    def run(self):
        cnt = 0
        while True:
            if cnt > 5 :
                self.finished.emit(cnt)
            cnt = cnt + 1
            time.sleep(1)

class Worker(QThread):
    finished2 = pyqtSignal(int)
    def __init__(self):
        super().__init__()
        self.avVal_worker = QAxWidget()
        self.avVal_worker.setControl("KHOPENAPI.KHOpenAPICtrl.1")

        self.avVal_worker.OnReceiveTrData.connect(self.receive_tr_data)

    def get_item_info(self):
        code = "005930"
        self.avVal_worker.dynamicCall("SetInputValue(QString, QString)", "종목코드", code)
        self.avVal_worker.dynamicCall("CommRqData(QString, QString, int, QString)", "opt10001_req", "opt10001", 0, "0101")

    def run(self):
        cnt = 0
        while True:
            print("hello", cnt)
            if cnt == 7:
                self.get_item_info()
                cnt = 0
            cnt = cnt + 1
            time.sleep(1)

    def receive_tr_data(self, screen_no, rqname, trcode, recordname, prev_next, data_len, err_code, msg1, msg2):
        print("data received.")
        print(trcode)
        print(data_len)
        if rqname == "opt10001_req":
            self.show_opt10001(rqname, trcode, recordname)
        # self.finished.emit(cnt)
        # print(rqname)
    def show_opt10001(self, rqname, trcode, recordname):
        # volume = self.kiwoom.dynamicCall("GetCommData(QString, QString, int, QString)", trcode, recordname, 0, "거래량")
        current_price = self.avVal_worker.dynamicCall("GetCommData(QString, QString, int, QString)", trcode, recordname, 0, "현재가")
        current_price = current_price.strip()
        current_price = int(current_price)

        self.finished2.emit(current_price)

class Kiwoom(QMainWindow):
    index = 0
    is_continue = 0
    def __init__(self):
        super().__init__()
        self.timer = Timer()
        self.timer.finished.connect(self.update_times)
        self.timer.start()

        self.worker = Worker()
        self.worker.finished2.connect(self.update_times2)
        self.worker.start()

        self.kiwoom = QAxWidget()
        self.kiwoom.setControl("KHOPENAPI.KHOpenAPICtrl.1")
        # self.kiwoom.dynamicCall("CommConnect()")      # login
        self.comm_connect()       # login

        self.kiwoom.OnEventConnect.connect(self.event_connect)
        self.kiwoom.OnReceiveTrData.connect(self.receive_tr_data)
        self.kiwoom.OnReceiveChejanData.connect(self.receive_chejan_data)

        self.init_UI()

    @pyqtSlot(int)
    def update_times(self, data) :
        self.text_edit4.setText(str(data))

    @pyqtSlot(int)
    def update_times2(self, data) :
        self.text_edit.append(str(data))
    
    def init_UI(self) :
        self.setWindowTitle("AutoK")
        self.setGeometry(150, 150, 1000, 500)

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

        self.tableWidget = QTableWidget(self)
        self.set_tableWidget()

        self.text_edit = QTextEdit(self)
        self.text_edit.setGeometry(10, 180, 190, 150)
        self.text_edit.setEnabled(False)    # 텍스트창의 내용물 활용여부 (False : 읽기모드)

        self.text_edit2 = QTextEdit(self)
        self.text_edit2.setGeometry(210, 180, 200, 150)
        self.text_edit2.setEnabled(False)    # 텍스트창의 내용물 활용여부 (False : 읽기모드)
        
        self.text_edit3 = QTextEdit(self)
        self.text_edit3.setGeometry(10, 340, 400, 150)
        self.text_edit3.setEnabled(False)    # 텍스트창의 내용물 활용여부 (False : 읽기모드)

        self.text_edit4 = QTextEdit(self)
        self.text_edit4.setGeometry(900, 15, 30, 30)
        self.text_edit4.setEnabled(False)    # 텍스트창의 내용물 활용여부 (False : 읽기모드)
        self.text_edit4.setStyleSheet("border-style : none;")

    def set_tableWidget(self):
        row_count = 8
        col_count = 5
        self.tableWidget.resize(550, 290)
        self.tableWidget.move(430, 50)
        self.tableWidget.setRowCount(row_count)
        self.tableWidget.setColumnCount(col_count)

        for i in range(int(row_count/2)):
            j=i*2
            self.tableWidget.setSpan(j,0,2,1)
            self.tableWidget.setSpan(j,1,2,1)
            self.tableWidget.setSpan(j,2,2,1)
            self.tableWidget.setSpan(j,4,2,1)

        self.tableWidget.verticalHeader().setVisible(False)
        self.tableWidget.setHorizontalHeaderItem(0, QTableWidgetItem("Code"))
        self.tableWidget.setHorizontalHeaderItem(1, QTableWidgetItem("Name"))
        self.tableWidget.setHorizontalHeaderItem(2, QTableWidgetItem("Count"))
        self.tableWidget.setHorizontalHeaderItem(3, QTableWidgetItem("Price"))
        self.tableWidget.setHorizontalHeaderItem(4, QTableWidgetItem("Percent"))

    def btn_test(self):
        print("test clicked")
        cnt = 0
        while cnt<10:
            if cnt == 3:
                self.btn_test2()
            self.text_edit.append(str(cnt))
            cnt = cnt + 1
            QtTest.QTest.qWait(1000)

    def btn_test2(self) :
        self.text_edit.append("BUYBUYBUY")
        

    def test2(self):
        self.i = 1
        
    def setTableWidgetData(self, row, col, content):
        item = QTableWidgetItem(content)
        item.setTextAlignment(QtCore.Qt.AlignVCenter | QtCore.Qt.AlignHCenter)
        self.tableWidget.setItem(row, col, item)
        # value = self.tableWidget.item(0,0)
        # print(value.text())
    ## [START] login ##
    def comm_connect(self):
        self.kiwoom.dynamicCall("CommConnect()")
        self.login_event_loop = QThread()
        self.login_event_loop.start()
    def event_connect(self, err_code):
        if err_code == 0:
            self.text_edit.append("login Success")
            self.login_event_loop.terminate()
        else:
            print("disconnected")
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
        print(rqname)

        if next == '2':
            self.remained_data = True
        else:
            self.remained_data = False

        if rqname == "opt10001_req":
            self.show_opt10001(rqname, trcode, recordname)

        if rqname == "opw00018_req":
            self.show_opw00018(rqname, trcode, recordname)

        if rqname == "opt10003_req":
            self.show_opt10003(rqname, trcode, recordname)

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
        print(data_cnt)

        for i in range(data_cnt) :
            total_percent = self.kiwoom.dynamicCall("GetCommData(QString, QString, int, QString)", trcode, recordname, i, "총수익률(%)")
            capital = self.kiwoom.dynamicCall("GetCommData(QString, QString, int, QString)", trcode, recordname, i, "추정예탁자산")
            itemcode = self.kiwoom.dynamicCall("GetCommData(QString, QString, int, QString)", trcode, recordname, i, "종목번호")
            itemname = self.kiwoom.dynamicCall("GetCommData(QString, QString, int, QString)", trcode, recordname, i, "종목명")
            each_percent = self.kiwoom.dynamicCall("GetCommData(QString, QString, int, QString)", trcode, recordname, i, "수익률(%)")
            cur_price = self.kiwoom.dynamicCall("GetCommData(QString, QString, int, QString)", trcode, recordname, i, "현재가")
            unit_price = self.kiwoom.dynamicCall("GetCommData(QString, QString, int, QString)", trcode, recordname, i, "매입가")
            est_price = self.kiwoom.dynamicCall("GetCommData(QString, QString, int, QString)", trcode, recordname, i, "평가금액")
            owncount = self.kiwoom.dynamicCall("GetCommData(QString, QString, int, QString)", trcode, recordname, i, "보유수량")

            self.setTableWidgetData(2*i, 0, itemcode)
            self.setTableWidgetData(2*i, 1, itemname)
            self.setTableWidgetData(2*i, 2, str(int(owncount)))
            self.setTableWidgetData((2*i + 1), 3, str(int(unit_price)))
            self.setTableWidgetData(2*i, 3, str(int(cur_price)))
            self.setTableWidgetData(2*i, 4, str(round(float(each_percent), 2)))

    def get_repeat_cnt(self, trcode, rqname):
        ret = self.kiwoom.dynamicCall("GetRepeatCnt(QString, QString)", trcode, rqname)
        return ret

if __name__=="__main__":
    app = QApplication(sys.argv)
    myWindow = Kiwoom()
    myWindow.show()
    app.exec_()