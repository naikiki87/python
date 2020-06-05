import sys
import time
import pandas as pd

from PyQt5.QtWidgets import *
from PyQt5.QAxContainer import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5 import QtTest, QtCore

class Worker(QThread):
    # finished2 = pyqtSignal(int)
    finished2 = pyqtSignal(dict)
    def __init__(self, acc_pw):
        super().__init__()
        self.acc_pw = acc_pw
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
            # self.finished2.emit(cnt)

            if cnt == 3 :
                self.get_item_info()
                cnt = 0
            cnt = cnt + 1
            # QtTest.QTest.qWait(1000)
            time.sleep(1)

    def receive_tr_data(self, screen_no, rqname, trcode, recordname, prev_next, data_len, err_code, msg1, msg2):
        i = 0
        print("data received.")
        if rqname == "opt10001_req":
            current_price = self.avVal_worker.dynamicCall("GetCommData(QString, QString, int, QString)", trcode, recordname, 0, "현재가")
            current_price = current_price.strip()
            current_price = int(current_price)

            sendDict = {}
            sendDict[(i, "cur_price")] = current_price

            self.finished2.emit(sendDict)