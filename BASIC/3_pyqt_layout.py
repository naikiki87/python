import sys
from PyQt5.QtWidgets import *
from PyQt5 import uic

form_class = uic.loadUiType("designer_test.ui")[0]

class WindowClass(QMainWindow, form_class) :
    def __init__(self) :
        super().__init__()
        self.setupUi(self)
        # self.btn1.clicked.connect(self.func_test)
        self.pushButton1.clicked.connect(self.func_test)

    def func_test(self) :
        print("button clicked")
        self.text_edit.append("Clicked")

if __name__=="__main__":
    app = QApplication(sys.argv)
    app.setStyle(QStyleFactory.create('Fusion')) # --> 없으면, 헤더색 변경 안됨.
    # print(sys.argv)
    myWindow = WindowClass()
    myWindow.show()
    app.exec_()