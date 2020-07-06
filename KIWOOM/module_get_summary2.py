import sys
import time
import pandas as pd

from PyQt5.QtWidgets import *
from PyQt5.QAxContainer import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5 import QtTest, QtCore

TAX = 0.0025
FEE_BUY = 0.0035
FEE_SELL = 0.0035

class Worker(QThread):
    connected = 0
    data_from_thread = pyqtSignal(int)
    rp_dict = pyqtSignal(dict)
    th_con = pyqtSignal(int)

    def __init__(self, seq):
        super().__init__()
        self.seq = seq
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
        self.lock = 0
        while True:
            try:
                print("con : ", self.connected)
                if self.connected == 1:
                    self.th_con.emit(1)
                    break

                time.sleep(1)
                
            except:
                pass
    
    @pyqtSlot("PyQt_PyObject")
    def data_from_main(self, data) :
        print(self.seq, " : ", data)

    # @pyqtSlot("PyQt_PyObject")
    @pyqtSlot(dict)
    def dict_from_main(self, data) :

        if self.lock == 0 :
            self.lock = 1       ## lock

            own_count = data['own_count']
            unit_price = data['unit_price']
            cur_price = data['cur_price']

            total_purchase = own_count * unit_price
            total_evaluation = own_count * cur_price
            temp_total = total_evaluation - total_purchase
            fee_buy = FEE_BUY * total_purchase
            fee_sell = FEE_SELL * total_evaluation
            tax = TAX * total_evaluation
            total_fee = round((fee_buy + fee_sell + tax), 1)
            total_sum = total_evaluation - total_purchase - total_fee
            percent = round((total_sum / total_purchase) * 100, 1)

            rp_dict = {}
            rp_dict.update(data)
            rp_dict['total_purchase'] = total_purchase
            rp_dict['total_evaluation'] = total_evaluation
            rp_dict['temp_total'] = temp_total
            rp_dict['total_fee'] = total_fee
            rp_dict['total_sum'] = total_sum
            rp_dict['percent'] = percent
            
            rp_dict['seq'] = self.seq

            self.rp_dict.emit(rp_dict)

            self.lock = 0       ## unlock

    def receive_tr_data(self, screen_no, rqname, trcode, recordname, prev_next, data_len, err_code, msg1, msg2):
        if rqname == "opt10001_req":
            print(" data received", rqname)


    def get_repeat_cnt(self, trcode, rqname):
        ret = self.worker.dynamicCall("GetRepeatCnt(QString, QString)", trcode, rqname)
        return ret