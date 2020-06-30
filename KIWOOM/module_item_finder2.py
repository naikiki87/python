import sys
import time
import pandas as pd

from PyQt5.QtWidgets import *
from PyQt5.QAxContainer import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5 import QtTest, QtCore

class Finder(QThread):
    msg_from_FINDER = pyqtSignal(str)

    def __init__(self, acc_pw):
        super().__init__()
        self.acc_password = acc_pw
        self.kiwoom = QAxWidget()
        self.kiwoom.setControl("KHOPENAPI.KHOpenAPICtrl.1")
        self.kiwoom.dynamicCall("CommConnect()")

        self.kiwoom.OnEventConnect.connect(self.event_connect)
        self.kiwoom.OnReceiveTrData.connect(self.receive_tr_data)

        self.init_ENV()     ## 환경 초기화

    def init_ENV(self) :
        self.connected = 0
        self.df_items = pd.DataFrame(columns = ['item_code', 'item_name'])

    def event_connect(self, err_code):
        if err_code == 0:
            self.connected = 1
        else:
            print("thread disconnected")
    def receive_tr_data(self, screen_no, rqname, trcode, recordname, prev_next, data_len, err_code, msg1, msg2):
        if rqname == "opw00018_req":
            # print("data received", rqname)
            data_cnt = self.get_repeat_cnt(trcode, rqname)
            self.summary_data.emit(sendDict)
        if rqname == "GET_ItemInfo":
            self.GET_ItemInfo(rqname, trcode, recordname)

    def GET_ItemInfo(self, rqname, trcode, recordname) :
        print("item info called")
        item_code = self.kiwoom.dynamicCall("GetCommData(QString, QString, int, QString)", trcode, recordname, 0, "종목코드")
        item_name = self.kiwoom.dynamicCall("GetCommData(QString, QString, int, QString)", trcode, recordname, 0, "종목명")

        print(item_code, " : ", item_name)

        # index = len(df_items)

        # self.df_items.loc[index] = [item_code.strip(), item_name.strip()]

    def get_repeat_cnt(self, trcode, rqname):
        ret = self.kiwoom.dynamicCall("GetRepeatCnt(QString, QString)", trcode, rqname)
        return ret

    def find_items(self) :
        item_list = self.kiwoom.dynamicCall("GetCodeListByMarket(QString)", "10")
        item_list = item_list.split(';')

        # print("cnt : ", len(item_list))
        # print("1 : ", item_list[0])

        for i in range(100) :
            item_code = item_list[i]
            print(i, item_code)
            self.kiwoom.dynamicCall("SetInputValue(QString, QString)", "종목코드", item_code)
            self.kiwoom.dynamicCall("CommRqData(QString, QString, int, QString)", "GET_ItemInfo", "opt10001", 0, "0101")

    def run(self):
        while True:
            try:
                print("con : ", self.connected)
                if self.connected == 1:
                    break
                time.sleep(1)
            except:
                pass

        self.msg_from_FINDER.emit("FINDER CONNECTED - WoRKING")
        # self.find_items()