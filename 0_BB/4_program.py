import sys
import sqlite3
import time
import math
import pandas as pd
import datetime
import config
from time import localtime, strftime
from PyQt5.QtWidgets import *
from PyQt5.QAxContainer import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5 import QtTest, QtCore, QtWidgets, uic, QtGui

form_class = uic.loadUiType("interface.ui")[0]

class BaseBall(QMainWindow, form_class):
    test_dict0 = pyqtSignal(dict)

    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.setWindowTitle("pyqt")
        self.init_ENV()


    def init_ENV(self) :
        ## button 동작 binding
        self.btn_TEST.clicked.connect(self.strike)
        self.btn_TEST_2.clicked.connect(self.ball)
        self.btn_TEST_3.clicked.connect(self.foul)
        self.btn_TEST_4.clicked.connect(self.hit)
        self.btn_H2.clicked.connect(self.hit2)
        self.btn_H3.clicked.connect(self.hit3)
        self.btn_HR.clicked.connect(self.hitHR)

        self.cnt_strike = 0
        self.cnt_ball = 0
        self.cnt_out = 0
        self.cnt_throw = 0

        self.show_count()
        ## table setting

    def show_count(self) :
        self.show_throw_cnt.setText(str(self.cnt_throw))

        self.show_strike.setText(str(self.cnt_strike))
        self.show_ball.setText(str(self.cnt_ball))
        self.show_out.setText(str(self.cnt_out))

    def strike(self) :
        print("strike")
        self.cnt_throw = self.cnt_throw + 1
        self.show_strike.setText("1")

        if self.cnt_strike == 2 :
            self.cnt_out = self.cnt_out + 1

            self.cnt_strike = 0
            self.cnt_ball = 0

            if self.cnt_out == 3 :
                self.cnt_out = 0        # reset out
                self.show_count()
                self.text_edit.setText("Change")
            
            else : 
                self.show_count()
        
        else :
            self.cnt_strike = self.cnt_strike + 1
            self.show_count()

    def ball(self) :
        print("ball")
        self.cnt_throw = self.cnt_throw + 1
        if self.cnt_ball == 3 :
            self.cnt_strike = 0
            self.cnt_ball = 0
            self.show_count()
        else :
            self.cnt_ball = self.cnt_ball + 1
            self.show_count()

    def foul(self) :
        print("foul")
        self.cnt_throw = self.cnt_throw + 1

        if self.cnt_strike < 2 :
            self.cnt_strike = self.cnt_strike + 1
        
        self.show_count()
    def hit(self) :
        print("hit")
        self.cnt_throw = self.cnt_throw + 1

        self.cnt_strike = 0
        self.cnt_ball = 0

        self.show_count()

    def hit2(self) :
        print("hit2")
        self.cnt_throw = self.cnt_throw + 1

        self.cnt_strike = 0
        self.cnt_ball = 0

        self.show_count()

    def hit3(self) :
        print("hit3")
        self.cnt_throw = self.cnt_throw + 1

        self.cnt_strike = 0
        self.cnt_ball = 0

        self.show_count()

    def hitHR(self) :
        print("hitHR")
        self.cnt_throw = self.cnt_throw + 1

        self.cnt_strike = 0
        self.cnt_ball = 0

        self.show_count()



    
if __name__=="__main__":
    app = QApplication(sys.argv)
    app.setStyle(QStyleFactory.create('Fusion')) # --> 없으면, 헤더색 변경 안됨.
    # print(now, "[MAIN]", sys.argv)
    myWindow = BaseBall()
    myWindow.show()
    app.exec_()
    