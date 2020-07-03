import sys
import time
import pandas as pd

from PyQt5.QtWidgets import *
from PyQt5.QAxContainer import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5 import QtTest, QtCore

# for i in range(10) :
#     globals()['DF_item{}'.format(i)] = pd.DataFrame(columns = ['code', 'price', 'm_1', 'm_2', 'm_3', 'm_4', 'm_5', 'm_6', 'm_7', 'm_8', 'm_9', 'm_10'])
#     globals()['save_times{}'.format(i)] = 0
#     globals()['elapsed_min{}'.format(i)] = 0


class Worker(QThread):
    connected = 0
    finished2 = pyqtSignal(dict)
    summary_data = pyqtSignal(dict)
    save_times = 0
    elapsed_min = 0
    save_times_init = 0

    def __init__(self):
        super().__init__()
        # self.item_code = item_code
        # self.seq = seq
        # self.acc_password = acc_pw
        self.worker = QAxWidget()
        self.worker.setControl("KHOPENAPI.KHOpenAPICtrl.1")
        self.worker.dynamicCall("CommConnect()")

        self.worker.OnEventConnect.connect(self.event_connect)
        self.worker.OnReceiveTrData.connect(self.receive_tr_data)
        self.worker.OnReceiveRealData.connect(self.receive_real_data)

    def event_connect(self, err_code):
        if err_code == 0:
            self.connected = 1
        else:
            print("thread disconnected")

    def get_item_info(self):
        code = "005930"
        self.worker.dynamicCall("SetInputValue(QString, QString)", "종목코드", code)
        self.worker.dynamicCall("CommRqData(QString, QString, int, QString)", "opt10001_req", "opt10001", 0, "0101")

    def get_summary(self):
        acc_no = "8137639811"
        acc_pw = self.acc_password
        
        if self.acc_password != "6458":
            # print("Wrong password")
            a = 1
        else :
            # print("Corret password")
            self.worker.dynamicCall("SetInputValue(QString, QString)", "계좌번호", acc_no)
            self.worker.dynamicCall("SetInputValue(QString, QString)", "비밀번호", self.acc_password)
            self.worker.dynamicCall("CommRqData(QString, QString, int, QString)", "opw00018_req", "opw00018", 0, "0101")
    def SetRealReg(self, screenNo, item_code, fid, realtype):
        print("worker : setrealreg")
        self.worker.dynamicCall("SetRealReg(QString, QString, QString, QString)", screenNo, item_code, fid, realtype)
    def run(self):
        while True:
            try:
                print("con : ", self.connected)
                if self.connected == 1:
                    break

                time.sleep(1)
                
            except:
                pass

        # self.set_real()

    def set_real(self) :
        print("set real")
        
        self.SetRealReg("0101", self.item_code, "10", 1)      # Real Time Data Registration
    
    def receive_real_data(self, code, real_type, real_data): 
        print(self.seq, "worker real receive : ", code)

    def receive_tr_data(self, screen_no, rqname, trcode, recordname, prev_next, data_len, err_code, msg1, msg2):
        print("tr data : ", rqname)
        if rqname == "opw00018_req":
            print("data received", rqname)
            data_cnt = self.get_repeat_cnt(trcode, rqname)

            total_purchase = self.worker.dynamicCall("GetCommData(QString, QString, int, QString)", trcode, recordname, 0, "총매입금액")
            total_evaluation = self.worker.dynamicCall("GetCommData(QString, QString, int, QString)", trcode, recordname, 0, "총평가금액")

            sendDict = {}
            sendDict["count"] = data_cnt
            sendDict["total_purchase"] = str('{0:,}'.format(int(total_purchase)))
            sendDict["total_evaluation"] = str('{0:,}'.format(int(total_evaluation)))

            for i in range(data_cnt) :
                total_percent = self.worker.dynamicCall("GetCommData(QString, QString, int, QString)", trcode, recordname, i, "총수익률(%)")
                capital = self.worker.dynamicCall("GetCommData(QString, QString, int, QString)", trcode, recordname, i, "추정예탁자산")
                item_code = self.worker.dynamicCall("GetCommData(QString, QString, int, QString)", trcode, recordname, i, "종목번호")
                item_name = self.worker.dynamicCall("GetCommData(QString, QString, int, QString)", trcode, recordname, i, "종목명")
                each_percent = self.worker.dynamicCall("GetCommData(QString, QString, int, QString)", trcode, recordname, i, "수익률(%)")
                cur_price = self.worker.dynamicCall("GetCommData(QString, QString, int, QString)", trcode, recordname, i, "현재가")
                unit_price = self.worker.dynamicCall("GetCommData(QString, QString, int, QString)", trcode, recordname, i, "매입가")
                total_purchase_price = self.worker.dynamicCall("GetCommData(QString, QString, int, QString)", trcode, recordname, i, "매입금액")
                total_evaluation_price = self.worker.dynamicCall("GetCommData(QString, QString, int, QString)", trcode, recordname, i, "평가금액")
                owncount = self.worker.dynamicCall("GetCommData(QString, QString, int, QString)", trcode, recordname, i, "보유수량")
                added_fee = self.worker.dynamicCall("GetCommData(QString, QString, int, QString)", trcode, recordname, i, "수수료합")
                tax = self.worker.dynamicCall("GetCommData(QString, QString, int, QString)", trcode, recordname, i, "세금")
                eval_pl = self.worker.dynamicCall("GetCommData(QString, QString, int, QString)", trcode, recordname, i, "평가손익")

                if globals()['save_times{}'.format(i)] == 20:
                    globals()['save_times{}'.format(i)] = 0
                    m_1 = globals()['DF_item{}'.format(i)]['price'].mean()
                    m_2 = globals()['DF_item{}'.format(i)].loc[0]['m_1']
                    m_3 = globals()['DF_item{}'.format(i)].loc[0]['m_2']
                    m_4 = globals()['DF_item{}'.format(i)].loc[0]['m_3']
                    m_5 = globals()['DF_item{}'.format(i)].loc[0]['m_4']
                    m_6 = globals()['DF_item{}'.format(i)].loc[0]['m_5']
                    m_7 = globals()['DF_item{}'.format(i)].loc[0]['m_6']
                    m_8 = globals()['DF_item{}'.format(i)].loc[0]['m_7']
                    m_9 = globals()['DF_item{}'.format(i)].loc[0]['m_8']
                    m_10 = globals()['DF_item{}'.format(i)].loc[0]['m_9']

                    globals()['DF_item{}'.format(i)].loc[globals()['save_times{}'.format(i)]] = [item_code, int(cur_price), m_1, m_2, m_3, m_4, m_5, m_6, m_7, m_8, m_9, m_10]
                    globals()['save_times{}'.format(i)] = globals()['save_times{}'.format(i)] + 1
                else:
                    globals()['DF_item{}'.format(i)].loc[globals()['save_times{}'.format(i)]] = [0, int(cur_price), 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
                    globals()['save_times{}'.format(i)] = globals()['save_times{}'.format(i)] + 1

                print(globals()['save_times{}'.format(i)])

                total_sum = str('{0:,}'.format(int(total_evaluation_price) - int(total_purchase_price)))
                owncount = str('{0:,}'.format(int(owncount)))
                cur_price = str('{0:,}'.format(int(cur_price)))
                unit_price = str('{0:,}'.format(int(unit_price)))
                total_evaluation_price = str('{0:,}'.format(int(total_evaluation_price)))
                total_purchase_price = str('{0:,}'.format(int(total_purchase_price)))
                total_fee = str('{0:,}'.format(int(float(added_fee) + float(tax))))
                eval_pl = str('{0:,}'.format(int(eval_pl)))
                each_percent = str(round(float(each_percent), 2))

                sendDict[(i, "item_code")] = item_code
                sendDict[(i, "item_name")] = item_name
                sendDict[(i, "total_sum")] = total_sum
                sendDict[(i, "owncount")] = owncount
                sendDict[(i, "cur_price")] = cur_price
                sendDict[(i, "unit_price")] = unit_price
                sendDict[(i, "total_evaluation_price")] = total_evaluation_price
                sendDict[(i, "total_purchase_price")] = total_purchase_price
                sendDict[(i, "total_fee")] = total_fee
                sendDict[(i, "eval_pl")] = eval_pl
                sendDict[(i, "each_percent")] = each_percent

                
                    
            # self.save_times = self.save_times + 1
            print(DF_item0)
            
            self.summary_data.emit(sendDict)

    def get_repeat_cnt(self, trcode, rqname):
        ret = self.worker.dynamicCall("GetRepeatCnt(QString, QString)", trcode, rqname)
        return ret