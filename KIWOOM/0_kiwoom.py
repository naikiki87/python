import sys
from PyQt5.QtWidgets import *
from PyQt5.QAxContainer import *
from PyQt5.QtCore import *
import time

TR_REQ_TIME_INTERVAL = 0.2

class Kiwoom(QAxWidget):
    def __init__(self):
        super().__init__()
        self._create_kiwoom_instance()
        self._set_signal_slots()

    def _create_kiwoom_instance(self):
        self.setControl("KHOPENAPI.KHOpenAPICtrl.1")

    def _set_signal_slots(self):
        self.OnEventConnect.connect(self._event_connect)
        self.OnReceiveTrData.connect(self._receive_tr_data)

    def comm_connect(self):
        self.dynamicCall("CommConnect()")
        self.login_event_loop = QEventLoop()
        self.login_event_loop.exec_()

    def _event_connect(self, err_code):
        if err_code == 0:
            print("connected")
        else:
            print("disconnected")

        self.login_event_loop.exit()

    def get_code_list_by_market(self, market):
        code_list = self.dynamicCall("GetCodeListByMarket(QString)", market)
        code_list = code_list.split(';')
        return code_list[:-1]

    def get_master_code_name(self, code):
        code_name = self.dynamicCall("GetMasterCodeName(QString)", code)
        return code_name

    def set_input_value(self, id, value):
        self.dynamicCall("SetInputValue(QString, QString)", id, value)

    def comm_rq_data(self, rqname, trcode, next, screen_no):
        self.dynamicCall("CommRqData(QString, QString, int, QString", rqname, trcode, next, screen_no)
        self.tr_event_loop = QEventLoop()
        self.tr_event_loop.exec_()

    def _comm_get_data(self, code, real_type, field_name, index, item_name):
        ret = self.dynamicCall("CommGetData(QString, QString, QString, int, QString", code,
                               real_type, field_name, index, item_name)
        return ret.strip()

    def _get_repeat_cnt(self, trcode, rqname):
        ret = self.dynamicCall("GetRepeatCnt(QString, QString)", trcode, rqname)
        return ret

    def _receive_tr_data(self, screen_no, rqname, trcode, record_name, next, unused1, unused2, unused3, unused4):
        if next == '2':
            self.remained_data = True
        else:
            self.remained_data = False

        if rqname == "opt10081_req":
            self._opt10081(rqname, trcode)

        if rqname == "opt10001_req":
            self._opt10001(rqname, trcode)

        if rqname == "opw00018_req":
            self._opw00018(rqname, trcode)

        try:
            self.tr_event_loop.exit()
        except AttributeError:
            pass

    def _opt10081(self, rqname, trcode):
        data_cnt = self._get_repeat_cnt(trcode, rqname)

        for i in range(data_cnt):
            date = self._comm_get_data(trcode, "", rqname, i, "일자")
            open = self._comm_get_data(trcode, "", rqname, i, "시가")
            high = self._comm_get_data(trcode, "", rqname, i, "고가")
            low = self._comm_get_data(trcode, "", rqname, i, "저가")
            close = self._comm_get_data(trcode, "", rqname, i, "현재가")
            volume = self._comm_get_data(trcode, "", rqname, i, "거래량")
            print(date, open, high, low, close, volume)

    def _opt10001(self, rqname, trcode):
        data_cnt = self._get_repeat_cnt(trcode, rqname)

        name = self._comm_get_data(trcode, "", rqname, 0, "종목명")
        volume = self._comm_get_data(trcode, "", rqname, 0, "거래량")
        numStocks = self._comm_get_data(trcode, "", rqname, 0, "상장주식")
        price = self._comm_get_data(trcode, "", rqname, 0, "시가")
        per = self._comm_get_data(trcode, "", rqname, 0, "PER")

        print("종목명 : ", name)
        print("거래량 : ", volume)
        print("상장주식 : ", numStocks)
        print("시가 : ", price)
        print("PER : ", per)

    def _opw00018(self, rqname, trcode):
        data_cnt = self._get_repeat_cnt(trcode, rqname)
        print("herer")

        # for i in range(data_cnt):
        percent = self._comm_get_data(trcode, "", rqname, 0, "총수익률(%)")
        capital = self._comm_get_data(trcode, "", rqname, 0, "추정예탁자산")
        print("총수익률 : ", percent)
        print("예탁자산 : ", capital)
        capital = float(capital)
        print("예탁자산2 : ", capital)
    
    def exe_opw00018(self, acc_no, password):
        self.set_input_value("계좌번호", acc_no)
        self.set_input_value("비밀번호", password)
        self.comm_rq_data("opw00018_req", "opw00018", 0, "0101")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    kiwoom = Kiwoom()
    kiwoom.comm_connect()

    ## opt10081 TR 요청
    # kiwoom.set_input_value("종목코드", "039490")
    # kiwoom.set_input_value("기준일자", "20170224")
    # kiwoom.set_input_value("수정주가구분", 1)
    # kiwoom.comm_rq_data("opt10081_req", "opt10081", 0, "0101")

    # while kiwoom.remained_data == True:
    #     time.sleep(TR_REQ_TIME_INTERVAL)
    #     kiwoom.set_input_value("종목코드", "039490")
    #     kiwoom.set_input_value("기준일자", "20170224")
    #     kiwoom.set_input_value("수정주가구분", 1)
    #     kiwoom.comm_rq_data("opt10081_req", "opt10081", 2, "0101")

    ## opt10001 - 주식정보 TR 요청
    # kiwoom.set_input_value("종목코드", "005930")
    # kiwoom.comm_rq_data("opt10001_req", "opt10001", 0, "0101")

    ## opw00018 - 계좌정보 TR 요청
    times = 0

    while times <= 5:
        kiwoom.exe_opw00018("8137639811", "6458")
        time.sleep(1)
        times = times + 1
    # kiwoom.set_input_value("계좌번호", "8137639811")
    # kiwoom.set_input_value("비밀번호", "6458")
    # kiwoom.comm_rq_data("opw00018_req", "opw00018", 0, "0101")