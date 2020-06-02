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

        self.setWindowTitle("opt10001")
        self.setGeometry(300, 300, 300, 200)


        label = QLabel('종목코드', self)
        label.move(20, 40)

        self.code_edit = QLineEdit(self)
        self.code_edit.move(80, 40)
        # self.code_edit.setText('종목코드를 입력하세요')

        btn0 = QPushButton('테스트', self)
        btn0.move(190, 10)
        btn0.clicked.connect(self.test_clicked)

        btn1 = QPushButton('조회', self)
        btn1.move(190, 40)
        btn1.clicked.connect(self.btn1_clicked)

        self.text_edit = QTextEdit(self)
        self.text_edit.setGeometry(10, 80, 280, 80)
        self.text_edit.setEnabled(False)    # 텍스트창의 내용물 활용여부 (False : 읽기모드)

    def event_connect(self, err_code):
        if err_code == 0:
            self.text_edit.append("login Success")

    def test_clicked(self):
        # ret = self.kiwoom.dynamicCall("GetCodeListByMarket(QString)", ["0"])
        # acc_cnt = self.kiwoom.dynamicCall("GetloginInfo(QString)", ["ACCOUNT_CNT"])
        # acc_num = self.kiwoom.dynamicCall("GetloginInfo(QString)", ["ACCNO"])
        # chejan = self.kiwoom.dynamicCall("GetChejanData(int)", 9201)

        self.kiwoom.dynamicCall("SetInputValue(QString, QString)", "계좌번호", "8137639811")
        self.kiwoom.dynamicCall("SetInputValue(QString, QString)", "비밀번호", "6458")

        self.kiwoom.dynamicCall("CommRqData(QString, QString, int, QString)", "opw00018_req", "opw00018", 0, "0101")

        time.sleep(3)

        # self.btn1_clicked()




        
        # print("ret", ret)
        # print("acc", acc_num)
        # print("chejan", chejan)

        # self.text_edit.append("계좌수:" + acc_cnt.strip())
        # self.text_edit.append("계좌명:" + acc_num.strip())
        # kospi_code_list = ret.split(';')
        # kospi_code_name_list = []

        # for x in kospi_code_list:
        #     name = self.kiwoom.dynamicCall("GetMasterCodeName(QString)", [x])
        #     kospi_code_name_list.append(x+ " : " + name)

        # self.listWidget.addItems(kospi_code_name_list)

    def btn1_clicked(self):

        
        # def setInterval(func):
        #     global index
        #     while index!=5:
        #         func()
        #         time.sleep(5)

        # while self.index <= 5 :
        #     if self.index == 0 or self.index == 2 or self.index == 4:
        #         code = "005380"

        #     if self.index == 1 or self.index == 3 or self.index == 5:
        #         code = "005930"

            code = self.code_edit.text()
            # print(code)
            self.text_edit.append("종목코드:" + code)
            if code == "005930" :
                self.kiwoom.dynamicCall("SetInputValue(QString, QString)", "종목코드", code)
                self.kiwoom.dynamicCall("CommRqData(QString, QString, int, QString)", "opt10001_req", "opt10001", 0, "0101")
            elif code == "005830" :
                self.text_edit.append("00055588830000")

            # self.index = self.index + 1
            # time.sleep(2)

        # self.index = 0


        # self.btn10_clicked()

    def btn10_clicked(self):
        print("btn10 clicked")
        code = "006120"
        self.text_edit.append("종목코드:" + code)

        # SetInputValue
        self.kiwoom.dynamicCall("SetInputValue(QString, QString)", "종목코드", code)
        # CommRqData
        self.kiwoom.dynamicCall("CommRqData(QString, QString, int, QString)", "opt10001_req", "opt10001", 0, "0101")

    def over10(self):
        print("OVER 10")

    def receive_tr_data(self, screen_no, rqname, trcode, recordname, prev_next, data_len, err_code, msg1, msg2):
        print("data received.")

        if rqname == "opt10001_req":
            print("data here")
            name = self.kiwoom.dynamicCall("GetCommData(QString, QString, int, QString)", trcode, recordname, 0, "종목명")
            volume = self.kiwoom.dynamicCall("GetCommData(QString, QString, int, QString)", trcode, recordname, 0, "거래량")
            numStocks = self.kiwoom.dynamicCall("GetCommData(QString, QString, int, QString)", trcode, recordname, 0, "상장주식")
            prices = self.kiwoom.dynamicCall("GetCommData(QString, QString, int, QString)", trcode, recordname, 0, "시가")
            valPER = self.kiwoom.dynamicCall("GetCommData(QString, QString, int, QString)", trcode, recordname, 0, "PER")

            # if int(volume) > 10:
            #     self.over10()

            self.text_edit.append("종목명:" + name.strip())
            self.text_edit.append("거래량:" + volume.strip())
            self.text_edit.append("상장주식:" + numStocks.strip())
            self.text_edit.append("시가:" + prices.strip())
            self.text_edit.append("PER:" + valPER.strip())

            print(self.index)
            print("종목명:" + name.strip())
            print("거래량:" + volume.strip())
            print("상장주식:" + numStocks.strip())
            print("시가:" + prices.strip())
            print("PER:" + valPER.strip())
            print()

        if rqname == "opw00018_req":
            percent = self.kiwoom.dynamicCall("GetCommData(QString, QString, int, QString)", trcode, recordname, 0, "총수익률(%)")
            capital = self.kiwoom.dynamicCall("GetCommData(QString, QString, int, QString)", trcode, recordname, 0, "추정예탁자산")

            self.text_edit.append("수익률:" + percent.strip())
            self.text_edit.append("자산:" + capital.strip())

if __name__=="__main__":
    app = QApplication(sys.argv)
    myWindow = Kiwoom()
    myWindow.show()
    app.exec_()