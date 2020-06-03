import sys
import time
import pandas as pd

from PyQt5.QtWidgets import *
from PyQt5.QAxContainer import *
from PyQt5.QtGui import *

class Kiwoom(QMainWindow):
    index = 0

    def __init__(self):
        super().__init__()
        self.kiwoom = QAxWidget()
        self.kiwoom.setControl("KHOPENAPI.KHOpenAPICtrl.1")
        self.kiwoom.dynamicCall("CommConnect()")      # login

        self.kiwoom.OnEventConnect.connect(self.event_connect)
        self.kiwoom.OnReceiveTrData.connect(self.receive_tr_data)
        self.kiwoom.OnReceiveChejanData.connect(self.receive_chejan_data)

        self.setWindowTitle("AutoK")
        self.setGeometry(150, 150, 420, 500)


        label = QLabel('종목코드', self)
        label.move(20, 10)
        self.code_edit = QLineEdit(self)
        self.code_edit.move(80, 10)

        label = QLabel('금액', self)
        label.move(20, 50)
        self.buy_price = QLineEdit(self)
        self.buy_price.move(80, 50)

        btn1 = QPushButton('조회', self)
        btn1.move(190, 10)
        btn1.clicked.connect(self.btn_item_info)

        btn1 = QPushButton('TEST', self)
        btn1.move(290, 10)
        btn1.clicked.connect(self.btn_test)

        btn0 = QPushButton('매수주문', self)
        btn0.move(190, 50)
        btn0.clicked.connect(self.btn_buy_order)

        btn0 = QPushButton('매도주문', self)
        btn0.move(290, 50)
        btn0.clicked.connect(self.btn_sell_order)


        label = QLabel('계좌번호', self)
        label.move(20, 90)
        self.input_acc_no = QLineEdit(self)
        self.input_acc_no.move(80, 90)

        label = QLabel('비밀번호', self)
        label.move(20, 140)
        self.input_acc_pw = QLineEdit(self)
        self.input_acc_pw.move(80, 140)

        btn0 = QPushButton('잔고조회', self)
        btn0.move(190, 140)
        btn0.clicked.connect(self.btn_balance)


        self.text_edit = QTextEdit(self)
        self.text_edit.setGeometry(10, 180, 400, 300)
        self.text_edit.setEnabled(False)    # 텍스트창의 내용물 활용여부 (False : 읽기모드)

    def comm_connect(self):
        self.kiwoom.dynamicCall("CommConnect()")
        # self.login_event_loop = QEventLoop()
        # self.login_event_loop.exec_()

    def event_connect(self, err_code):
        if err_code == 0:
            self.text_edit.append("login Success")

    # def send_order(self, rqname, screen_no, acc_no, order_type, item_code, qty, price, hogagb, orgorderno):
    
    def btn_test(self):
        self.kiwoom.dynamicCall("SetInputValue(QString, QString)", "종목코드", "005930")
        self.kiwoom.dynamicCall("CommRqData(QString, QString, int, QString)", "opt10003_req", "opt10003", 0, "0101")


    def btn_buy_order(self):
        print("send order")
        rqname = "RQ_TEST"
        screen_no = "0101"
        acc_no = "8137639811"
        order_type = 1
        # item_code = "005930"
        item_code = self.code_edit.text()
        qty = 1
        price = 56000
        hogagb = "00"
        orgorderno = ""
        
        order = self.kiwoom.dynamicCall("SendOrder(QString, QString, QString, int, QString, int, int, QString, QString)",
                     [rqname, screen_no, acc_no, order_type, item_code, qty, price, hogagb, orgorderno])

    def btn_sell_order(self):
        print("send order")
        rqname = "RQ_TEST"
        screen_no = "0101"
        acc_no = "8137639811"
        order_type = 2
        # item_code = "005930"
        item_code = self.code_edit.text()
        qty = 1
        price = 110000
        hogagb = "00"
        orgorderno = ""
        
        order = self.kiwoom.dynamicCall("SendOrder(QString, QString, QString, int, QString, int, int, QString, QString)",
                     [rqname, screen_no, acc_no, order_type, item_code, qty, price, hogagb, orgorderno])
        
    def get_chejan_data(self, fid):
        ret = self.kiwoom.dynamicCall("GetChejanData(int)", fid)
        return ret

    def receive_chejan_data(self, gubun, item_cnt, fid_list):
        if gubun == "0" :
            self.text_edit.append("체결완료")
        # print(gubun)
        print("계좌번호 : ", self.get_chejan_data(9201))
        print("주문번호 : ", self.get_chejan_data(9203))
        print("종목명 : ", self.get_chejan_data(302))
        print("주문수량 : ", self.get_chejan_data(900))
        print("주문가격 : ", self.get_chejan_data(901))
        print("미체결수량 : ", self.get_chejan_data(902))
        print("체결가 : ", self.get_chejan_data(910), "체결량 : ", self.get_chejan_data(911))
        print("체결단가 : ", self.get_chejan_data(931))
        print()

        # self.text_edit.append(gubun)

        # self.text_edit.append("수익률:" + percent.strip())
        # self.text_edit.append("자산:" + capital.strip())

    def btn_item_info(self):
        code = self.code_edit.text()
        self.text_edit.append("종목코드:" + code)
        self.kiwoom.dynamicCall("SetInputValue(QString, QString)", "종목코드", code)
        self.kiwoom.dynamicCall("CommRqData(QString, QString, int, QString)", "opt10001_req", "opt10001", 0, "0101")

    
    def btn_balance(self):

        while self.index < 5 :

            acc_no = "8137639811"
            acc_pw = "6458"
            
            self.kiwoom.dynamicCall("SetInputValue(QString, QString)", "계좌번호", acc_no)
            self.kiwoom.dynamicCall("SetInputValue(QString, QString)", "비밀번호", acc_pw)
            self.kiwoom.dynamicCall("CommRqData(QString, QString, int, QString)", "opw00018_req", "opw00018", 0, "0101")

            self.index = self.index + 1

            time.sleep(0.2)


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
        name = self.kiwoom.dynamicCall("GetCommData(QString, QString, int, QString)", trcode, recordname, 0, "종목명")
        volume = self.kiwoom.dynamicCall("GetCommData(QString, QString, int, QString)", trcode, recordname, 0, "거래량")
        numStocks = self.kiwoom.dynamicCall("GetCommData(QString, QString, int, QString)", trcode, recordname, 0, "상장주식")
        prices = self.kiwoom.dynamicCall("GetCommData(QString, QString, int, QString)", trcode, recordname, 0, "시가")
        per = self.kiwoom.dynamicCall("GetCommData(QString, QString, int, QString)", trcode, recordname, 0, "PER")
        current_price = self.kiwoom.dynamicCall("GetCommData(QString, QString, int, QString)", trcode, recordname, 0, "현재가")

        self.text_edit.append("종목명:" + name.strip())
        self.text_edit.append("거래량:" + volume.strip())
        self.text_edit.append("상장주식:" + numStocks.strip())
        self.text_edit.append("시가:" + prices.strip())
        self.text_edit.append("PER:" + per.strip())
        self.text_edit.append("현재가:" + current_price.strip())

    def show_opw00018(self, rqname, trcode, recordname):
        data_cnt = self.get_repeat_cnt(trcode, rqname)

        for i in range(data_cnt) :
            percent = self.kiwoom.dynamicCall("GetCommData(QString, QString, int, QString)", trcode, recordname, i, "총수익률(%)")
            capital = self.kiwoom.dynamicCall("GetCommData(QString, QString, int, QString)", trcode, recordname, i, "추정예탁자산")
            itemcode = self.kiwoom.dynamicCall("GetCommData(QString, QString, int, QString)", trcode, recordname, i, "종목번호")
            owncount = self.kiwoom.dynamicCall("GetCommData(QString, QString, int, QString)", trcode, recordname, i, "보유수량")

        print(self.index)

        self.text_edit.append(str(self.index))
        # self.text_edit.append("수익률:" + percent.strip())
        # self.text_edit.append("자산:" + capital.strip())
        # self.text_edit.append("종목번호:" + itemcode.strip())
        # self.text_edit.append("보유수량:" + owncount.strip())

        print(percent, capital, itemcode, owncount)

    def get_repeat_cnt(self, trcode, rqname):
        ret = self.kiwoom.dynamicCall("GetRepeatCnt(QString, QString)", trcode, rqname)
        return ret

    # def show_opt10003(self, rqname, trcode, recordname):
    #     data_cnt = self.get_repeat_cnt(trcode, rqname)
    #     print("data cnt : ", data_cnt)

    #     for i in range(data_cnt):
    #         data = self.kiwoom.dynamicCall("GetCommData(QString, QString, int, QString)", trcode, recordname, i, "시간")
    #         print(i, data)

if __name__=="__main__":
    app = QApplication(sys.argv)
    myWindow = Kiwoom()
    # myWindow.comm_connect()
    myWindow.show()
    app.exec_()