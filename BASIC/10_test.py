import sys 
from PyQt5.QtWidgets import *
from PyQt5.QAxContainer import *
from PyQt5.QtCore import *
import datetime


class MyWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("주식호가잔량")
        self.setGeometry(300, 300, 300, 400)

        self.ocx = QAxWidget("KHOPENAPI.KHOpenAPICtrl.1")
        self.ocx.OnEventConnect.connect(self._handler_login)
        self.ocx.OnReceiveRealData.connect(self._handler_real_data)

        btn = QPushButton("구독", self)
        btn.move(20, 20)
        btn.clicked.connect(self.btn_clicked)

        btn2 = QPushButton("해지", self)
        btn2.move(180, 20)
        btn2.clicked.connect(self.btn2_clicked)

        # 2초 후에 로그인 진행
        QTimer.singleShot(1000 * 2, self.CommmConnect)


    def btn_clicked(self):
        self.SetRealReg("1000", "042670", "41", 0)

    def btn2_clicked(self):
        self.DisConnectRealData("1000") 

    def CommmConnect(self):
        self.ocx.dynamicCall("CommConnect()")
        self.statusBar().showMessage("login 중 ...")

    def _handler_login(self, err_code):
        if err_code == 0:
            self.statusBar().showMessage("login 완료")

    def _handler_real_data(self, code, real_type, data):
        if real_type == "주식호가잔량":
            hoga_time =  self.GetCommRealData(code, 21)         
            ask01_price =  self.GetCommRealData(code, 41)         
            ask01_volume =  self.GetCommRealData(code, 61)         
            bid01_price =  self.GetCommRealData(code, 51)         
            bid01_volume =  self.GetCommRealData(code, 71)         

            ratio_ask_bid = round((int(ask01_volume) / int(bid01_volume)), 2)

            print(hoga_time)
            print(f"매도호가: {ask01_price} - {ask01_volume}")
            print(f"매수호가: {bid01_price} - {bid01_volume}")
            print("ratio : ", ratio_ask_bid)

    def SetRealReg(self, screen_no, code_list, fid_list, real_type):
        self.ocx.dynamicCall("SetRealReg(QString, QString, QString, QString)", 
                              screen_no, code_list, fid_list, real_type)
        self.statusBar().showMessage("구독 신청 완료")

    def DisConnectRealData(self, screen_no):
        self.ocx.dynamicCall("DisConnectRealData(QString)", screen_no)
        self.statusBar().showMessage("구독 해지 완료")

    def GetCommRealData(self, code, fid):
        data = self.ocx.dynamicCall("GetCommRealData(QString, int)", code, fid) 
        return data


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MyWindow()
    window.show()
    app.exec_()