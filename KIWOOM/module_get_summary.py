import sys
import time
import pandas as pd

from PyQt5.QtWidgets import *
from PyQt5.QAxContainer import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5 import QtTest, QtCore, QtWidgets

class Worker(QThread):
    data = pyqtSignal(dict)
    # def __init__(self, acc_pw):
    def __init__(self):
        super().__init__()
        self.acc_pw = "6458"

        self.get_summary = QAxWidget()
        self.get_summary.setControl("KHOPENAPI.KHOpenAPICtrl.1")
        self.get_summary.OnReceiveTrData.connect(self.receive_tr_data)

    def get_summary(self):
        print("called get Summary")
        acc_no = "8137639811"
        acc_pw = self.acc_pw
        # acc_pw = self.input_acc_pw.text()
        if acc_pw != "6458":
            print("Wrong password")
        else :
            self.is_continue = 1
            while self.is_continue:
                self.get_summary.dynamicCall("SetInputValue(QString, QString)", "계좌번호", acc_no)
                self.get_summary.dynamicCall("SetInputValue(QString, QString)", "비밀번호", acc_pw)
                self.get_summary.dynamicCall("CommRqData(QString, QString, int, QString)", "opw00018_req", "opw00018", 0, "0101")
                # QtTest.QTest.qWait(3000)


    def run(self):
        cnt = 0
        while True:
            print(cnt)
            if cnt == 3 :
                
                self.get_summary()
                cnt = 0
            cnt = cnt + 1
            time.sleep(1)

    
    def receive_tr_data(self, screen_no, rqname, trcode, recordname, prev_next, data_len, err_code, msg1, msg2):
        i = 0
        print("data received.")
        if rqname == "opw00018_req":

            data_cnt = self.get_repeat_cnt(trcode, rqname)

            total_purchase = self.kiwoom.dynamicCall("GetCommData(QString, QString, int, QString)", trcode, recordname, 0, "총매입금액")
            total_evaluation = self.kiwoom.dynamicCall("GetCommData(QString, QString, int, QString)", trcode, recordname, 0, "총평가금액")

            sendDict = {}
            sendDict["total_purchase"] = str(int(total_purchase))
            sendDict["total_evaluation"] = str(int(total_evaluation))

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

                total_sum = str('{0:,}'.format(int(total_evaluation_price) - int(total_purchase_price)))
                owncount = str('{0:,}'.format(int(owncount)))
                cur_price = str('{0:,}'.format(int(cur_price)))
                unit_price = str('{0:,}'.format(int(unit_price)))
                total_evaluation_price = str('{0:,}'.format(int(total_evaluation_price)))
                total_purchase_price = str('{0:,}'.format(int(total_purchase_price)))
                total_fee = str('{0:,}'.format(int(float(added_fee) + float(tax))))
                eval_pl = str('{0:,}'.format(int(eval_pl)))

                sendDict[(i, "total_sum")] = total_sum
                sendDict[(i, "owncount")] = owncount
                sendDict[(i, "cur_price")] = cur_price
                sendDict[(i, "unit_price")] = unit_price
                sendDict[(i, "total_evaluation_price")] = total_evaluation_price
                sendDict[(i, "total_purchase_price")] = total_purchase_price
                sendDict[(i, "total_fee")] = total_fee
                sendDict[(i, "eval_pl")] = eval_pl

            self.data.emit(sendDict)

    def get_repeat_cnt(self, trcode, rqname):
        ret = self.get_summary.dynamicCall("GetRepeatCnt(QString, QString)", trcode, rqname)
        return ret