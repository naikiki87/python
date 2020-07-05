import sys
import time
import pandas as pd

from PyQt5.QtWidgets import *
from PyQt5.QAxContainer import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5 import QtTest, QtCore

class Worker(QThread):
    connected = 0
    data_from_thread = pyqtSignal(int)
    rp_dict = pyqtSignal(dict)

    def __init__(self):
        super().__init__()
        # self.seq = seq
        self.worker = QAxWidget()
        self.worker.setControl("KHOPENAPI.KHOpenAPICtrl.1")
        self.worker.dynamicCall("CommConnect()")

        self.worker.OnEventConnect.connect(self.event_connect)
        self.worker.OnReceiveTrData.connect(self.receive_tr_data)

    def event_connect(self, err_code):
        if err_code == 0:
            self.connected = 1
        else:
            print("thread disconnected")

    def get_item_info(self):
        code = "005930"
        self.worker.dynamicCall("SetInputValue(QString, QString)", "종목코드", code)
        self.worker.dynamicCall("CommRqData(QString, QString, int, QString)", "opt10001_req", "opt10001", 0, "0101")

    def run(self):
        while True:
            try:
                print("con : ", self.connected)
                if self.connected == 1:
                    break

                time.sleep(1)
                
            except:
                pass

        # self.data_from_thread.emit(100)
        # while True:
        #     try :
        #         self.get_item_info()
        #         # print("HELLO")
        #         QtTest.QTest.qWait(4000)
        #     except:
        #         pass
    
    @pyqtSlot("PyQt_PyObject")
    def data_from_main(self, data) :
        print(data)

    @pyqtSlot("PyQt_PyObject")
    def dict_from_main(self, data) :
        own = data['own']
        unit = data['unit']
        val = data['val']

        print("own : ", own)

        rp_dict = {}

        rp_dict.update(data)
        rp_dict['a'] = own * 10

        self.rp_dict.emit(rp_dict)


    def receive_tr_data(self, screen_no, rqname, trcode, recordname, prev_next, data_len, err_code, msg1, msg2):
        if rqname == "opt10001_req":
            print(" data received", rqname)


    def get_repeat_cnt(self, trcode, rqname):
        ret = self.worker.dynamicCall("GetRepeatCnt(QString, QString)", trcode, rqname)
        return ret