import sys
import sqlite3
import time
import math
import random
import pandas as pd
# import datetime
# import config
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
        self.btn_Fly.clicked.connect(self.fly)
        self.btn_TEST_4.clicked.connect(self.hit)
        self.btn_H2.clicked.connect(self.hit2)
        self.btn_H3.clicked.connect(self.hit3)
        self.btn_HR.clicked.connect(self.hitHR)
        self.btn_HIT_TEST.clicked.connect(self.hitTEST)

        self.base = [0, 0, 0, 0]
        self.score = 0

        self.cnt_strike = 0
        self.cnt_ball = 0
        self.cnt_out = 0
        self.cnt_throw = 0

        self.show_count()
        self.show_base()

        self.hit_direction = 0
        self.hit_land_pos = 0
        self.hit_high = 0
        self.hit_speed = 0
        ## table setting

    def show_base(self) :
        self.show_score.setText(str(self.score))
        if self.base[1] == 1 :
            self.base1.setText("■")
        elif self.base[1] == 0 :
            self.base1.setText("")
        if self.base[2] == 1 :
            self.base2.setText("■")
        elif self.base[2] == 0 :
            self.base2.setText("")
        if self.base[3] == 1 :
            self.base3.setText("■") 
        elif self.base[3] == 0 :
            self.base3.setText("")

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
    def fly(self) :
        print("fly")
        self.cnt_throw = self.cnt_throw + 1

        self.cnt_strike = 0
        self.cnt_ball = 0
        self.cnt_out = self.cnt_out + 1

        self.show_count()

    def run(self, hit) :
        print("run : ", hit)
        print("base : ", self.base)
        if self.base == [0,0,0,0] :
            if hit == 4 :
                self.score = self.score + 1
                self.base = [0,0,0,0]
            else :
                self.base[hit] = 1
                print("hithit : ", self.base)

        elif self.base == [0,1,0,0] :
            if hit == 4 :
                self.score = self.score + 2
                self.base = [0,0,0,0]
            elif hit == 3 : 
                self.score = self.score + 1
                self.base = [0,0,0,1]

        elif self.base == [0,0,1,0] :
            if hit == 4 :
                self.score = self.score + 2
                self.base = [0,0,0,0]
            elif hit == 3 : 
                self.score = self.score + 1
                self.base = [0,0,0,1]
        
        elif self.base == [0,0,0,1] :
            if hit == 4 :
                self.score = self.score + 2
                self.base = [0,0,0,0]
            elif hit == 3 : 
                self.score = self.score + 1
                self.base = [0,0,0,1]
            elif hit == 2 :
                self.score = self.score + 1
                self.base = [0,0,1,0]
            elif hit == 1 :
                print("9999")
                self.score = self.score + 1
                self.base = [0,1,0,0]
        
        elif self.base == [0,1,1,0] :
            if hit == 4 :
                self.score = self.score + 3
                self.base = [0,0,0,0]
            elif hit == 3 : 
                self.score = self.score + 2
                self.base = [0,0,0,1]
        
        elif self.base == [0,1,0,1] :
            if hit == 4 :
                self.score = self.score + 3
                self.base = [0,0,0,0]
            elif hit == 3 : 
                self.score = self.score + 2
                self.base = [0,0,0,1]
        
        elif self.base == [0,0,1,1] :
            if hit == 4 :
                self.score = self.score + 3
                self.base = [0,0,0,0]
            elif hit == 3 : 
                self.score = self.score + 2
                self.base = [0,0,0,1]
        
        elif self.base == [0,1,1,1] :
            if hit == 4 :
                self.score = self.score + 4
                self.base = [0,0,0,0]
            elif hit == 3 : 
                self.score = self.score + 3
                self.base = [0,0,0,1]

        self.show_base() 
    
    def hitTEST(self) :
        judge = ""
        post = ""
        temp = 0
        self.hit_direction = random.randint(1, 7)
        if self.hit_direction == 1 :
            judge = judge + "deep left "
        elif self.hit_direction == 2 :
            judge = judge + "left "
        elif self.hit_direction == 3 :
            judge = judge + "left <-> center "
        elif self.hit_direction == 4 :
            judge = judge + "center "
        elif self.hit_direction == 5 :
            judge = judge + "center <-> right "
        elif self.hit_direction == 6 :
            judge = judge + "right "
        elif self.hit_direction == 7 :
            judge = judge + "deep right "

        self.hit_land_pos = random.randint(1, 6)
        if self.hit_land_pos == 1 :
            judge = judge + "infield "
            self.hit_high = random.randint(-1, 0)
            if self.hit_high == -1 :
                judge = judge + "Ground Foul"
            elif self.hit_high == 0 :
                judge = judge + "Ground"
                if self.hit_direction <= 2 :
                    temp = random.randint(1, 100)
                    if temp <= 80 :
                        post = post + "OUT : 3rd -> 1st"
                    else :
                        post = post + "SAFE : infield hit"
                elif self.hit_direction <= 5 :
                    temp = random.randint(1, 100)
                    if temp <= 15 :
                        post = post + "OUT : P -> 1st"
                    elif temp <= 40 :
                        post = post + "OUT : 2nd -> 1st"
                    elif temp <= 65 :
                        post = post + "OUT : SS -> 1st"
                    elif temp <= 85 :
                        post = post + "HIT"
                    else :
                        post = post + "SAFE : infield hit"
                elif self.hit_direction <= 7 :
                    temp = random.randint(1, 100)
                    if temp <= 80 :
                        post = post + "OUT : 1st"
                    else :
                        post = post + "SAFE : infield hit"
        
        elif self.hit_land_pos == 2 :
            judge = judge + "infielder position "
            self.hit_high = random.randint(0, 9)
            if self.hit_high <= 3 :
                judge = judge + "Ground"
                if self.hit_direction <= 2 :
                    temp = random.randint(1, 100)
                    if temp <= 80 :
                        post = post + "OUT : 3rd -> 1st"
                    else :
                        post = post + "SAFE : infield hit"
                elif self.hit_direction <= 5 :
                    temp = random.randint(1, 100)
                    if temp <= 15 :
                        post = post + "OUT : P -> 1st"
                    elif temp <= 40 :
                        post = post + "OUT : 2nd -> 1st"
                    elif temp <= 65 :
                        post = post + "OUT : SS -> 1st"
                    elif temp <= 85 :
                        post = post + "HIT"
                    else :
                        post = post + "SAFE : infield hit"
                elif self.hit_direction <= 7 :
                    temp = random.randint(1, 100)
                    if temp <= 80 :
                        post = post + "OUT : 1st"
                    else :
                        post = post + "SAFE : infield hit"
            
            
            elif self.hit_high <= 6 :
                judge = judge + "line-drive"
                if self.hit_direction <= 2 :
                    temp = random.randint(1, 100)
                    if temp <= 80 :
                        post = post + "OUT : 3rd catch"
                    else :
                        post = post + "SAFE : infield hit"
                elif self.hit_direction <= 5 :
                    temp = random.randint(1, 100)
                    if temp <= 10 :
                        post = post + "OUT : P catch"
                    elif temp <= 40 :
                        post = post + "OUT : 2nd catch"
                    elif temp <= 70 :
                        post = post + "OUT : SS catch"
                    else :
                        post = post + "SAFE : infield hit"
                elif self.hit_direction <= 7 :
                    temp = random.randint(1, 100)
                    if temp <= 80 :
                        post = post + "OUT : 1st catch"
                    else :
                        post = post + "SAFE : infield hit"
            
            
            elif self.hit_high <= 9 :
                judge = judge + "high"
                if self.hit_direction <= 2 :
                    temp = random.randint(1, 100)
                    if temp <= 90 :
                        post = post + "OUT : 3rd catch"
                    else :
                        post = post + "SAFE : infield hit"
                elif self.hit_direction <= 5 :
                    temp = random.randint(1, 100)
                    if temp <= 5 :
                        post = post + "OUT : P catch"
                    elif temp <= 40 :
                        post = post + "OUT : 2nd catch"
                    elif temp <= 75 :
                        post = post + "OUT : SS catch"
                    else :
                        post = post + "SAFE : infield hit"
                elif self.hit_direction <= 7 :
                    temp = random.randint(1, 100)
                    if temp <= 90 :
                        post = post + "OUT : 1st catch"
                    else :
                        post = post + "SAFE : infield hit"

        elif self.hit_land_pos == 3 :
            judge = judge + "in <-> out "
            self.hit_high = random.randint(1, 9)
            
            
            if self.hit_high <= 3 :
                judge = judge + "line-drive"
                if self.hit_direction <= 2 :
                    temp = random.randint(1, 100)
                    if temp <= 35 :
                        post = post + "OUT : 3rd catch"
                    elif temp <= 40 :
                        post = post + "OUT : LF catch"
                    else :
                        post = post + "HIT"
                elif self.hit_direction <= 5 :
                    temp = random.randint(1, 100)
                    if temp <= 18 :
                        post = post + "OUT : SS catch"
                    elif temp <= 36 :
                        post = post + "OUT : 2nd catch"
                    elif temp <= 54 :
                        post = post + "OUT : CF catch"
                    else :
                        post = post + "HIT"
                elif self.hit_direction <= 7 :
                    temp = random.randint(1, 100)
                    if temp <= 35 :
                        post = post + "OUT : 1st catch"
                    elif temp <= 40 :
                        post = post + "OUT : RF catch"
                    else :
                        post = post + "HIT"

            
            
            elif self.hit_high <= 6 :
                judge = judge + "mid-high"
                if self.hit_direction <= 2 :
                    temp = random.randint(1, 100)
                    if temp <= 5 :
                        post = post + "OUT : 3rd catch"
                    elif temp <= 30 :
                        post = post + "OUT : LF catch"
                    else :
                        post = post + "HIT"
                elif self.hit_direction <= 5 :
                    temp = random.randint(1, 100)
                    if temp <= 5 :
                        post = post + "OUT : SS catch"
                    elif temp <= 10 :
                        post = post + "OUT : 2nd catch"
                    elif temp <= 15 :
                        post = post + "OUT : CF catch"
                    else :
                        post = post + "HIT"
                elif self.hit_direction <= 7 :
                    temp = random.randint(1, 100)
                    if temp <= 5 :
                        post = post + "OUT : 1st catch"
                    elif temp <= 30 :
                        post = post + "OUT : RF catch"
                    else :
                        post = post + "HIT"



            elif self.hit_high <= 9 :
                judge = judge + "high"
                if self.hit_direction <= 2 :
                    temp = random.randint(1, 100)
                    if temp <= 15 :
                        post = post + "OUT : 3rd catch"
                    elif temp <= 50 :
                        post = post + "OUT : LF catch"
                    else :
                        post = post + "HIT"
                elif self.hit_direction <= 5 :
                    temp = random.randint(1, 100)
                    if temp <= 20 :
                        post = post + "OUT : SS catch"
                    elif temp <= 40 :
                        post = post + "OUT : 2nd catch"
                    elif temp <= 70 :
                        post = post + "OUT : CF catch"
                    else :
                        post = post + "HIT"
                elif self.hit_direction <= 7 :
                    temp = random.randint(1, 100)
                    if temp <= 15 :
                        post = post + "OUT : 1st catch"
                    elif temp <= 50 :
                        post = post + "OUT : RF catch"
                    else :
                        post = post + "HIT"





        elif self.hit_land_pos == 4 :
            judge = judge + "outfielder position "
            self.hit_high = random.randint(1, 9)
            if self.hit_high <= 3 :
                judge = judge + "line-drive"
                if self.hit_direction <= 2 :
                    temp = random.randint(1, 100)
                    if temp <= 55 :
                        post = post + "OUT : LF catch"
                    else :
                        post = post + "HIT"
                elif self.hit_direction <= 5 :
                    temp = random.randint(1, 100)
                    if temp <= 55 :
                        post = post + "OUT : CF catch"
                    else :
                        post = post + "HIT"
                elif self.hit_direction <= 7 :
                    temp = random.randint(1, 100)
                    if temp <= 55 :
                        post = post + "OUT : RF catch"
                    else :
                        post = post + "HIT"




            elif self.hit_high <= 6 :
                judge = judge + "mid-high"
                if self.hit_direction <= 2 :
                    temp = random.randint(1, 100)
                    if temp <= 75 :
                        post = post + "OUT : LF catch"
                    else :
                        post = post + "HIT"
                elif self.hit_direction <= 5 :
                    temp = random.randint(1, 100)
                    if temp <= 75 :
                        post = post + "OUT : CF catch"
                    else :
                        post = post + "HIT"
                elif self.hit_direction <= 7 :
                    temp = random.randint(1, 100)
                    if temp <= 75 :
                        post = post + "OUT : RF catch"
                    else :
                        post = post + "HIT"



            elif self.hit_high <= 9 :
                judge = judge + "high"
                if self.hit_direction <= 2 :
                    temp = random.randint(1, 100)
                    if temp <= 85 :
                        post = post + "OUT : LF catch"
                    else :
                        post = post + "HIT"
                elif self.hit_direction <= 5 :
                    temp = random.randint(1, 100)
                    if temp <= 85 :
                        post = post + "OUT : CF catch"
                    else :
                        post = post + "HIT"
                elif self.hit_direction <= 7 :
                    temp = random.randint(1, 100)
                    if temp <= 85 :
                        post = post + "OUT : RF catch"
                    else :
                        post = post + "HIT"





        elif self.hit_land_pos == 5 :
            judge = judge + "over the outfielder "
            self.hit_high = random.randint(1, 9)
            if self.hit_high <= 3 :
                judge = judge + "line-drive"
                if self.hit_direction <= 2 :
                    temp = random.randint(1, 100)
                    if temp <= 15 :
                        post = post + "OUT : LF catch"
                    else :
                        post = post + "HIT"
                elif self.hit_direction <= 5 :
                    temp = random.randint(1, 100)
                    if temp <= 15 :
                        post = post + "OUT : CF catch"
                    else :
                        post = post + "HIT"
                elif self.hit_direction <= 7 :
                    temp = random.randint(1, 100)
                    if temp <= 15 :
                        post = post + "OUT : RF catch"
                    else :
                        post = post + "HIT"


            elif self.hit_high <= 6 :
                judge = judge + "mid-high"
                if self.hit_direction <= 2 :
                    temp = random.randint(1, 100)
                    if temp <= 30 :
                        post = post + "OUT : LF catch"
                    else :
                        post = post + "HIT"
                elif self.hit_direction <= 5 :
                    temp = random.randint(1, 100)
                    if temp <= 30 :
                        post = post + "OUT : CF catch"
                    else :
                        post = post + "HIT"
                elif self.hit_direction <= 7 :
                    temp = random.randint(1, 100)
                    if temp <= 30 :
                        post = post + "OUT : RF catch"
                    else :
                        post = post + "HIT"
            elif self.hit_high <= 9 :
                judge = judge + "high"
                if self.hit_direction <= 2 :
                    temp = random.randint(1, 100)
                    if temp <= 55 :
                        post = post + "OUT : LF catch"
                    else :
                        post = post + "HIT"
                elif self.hit_direction <= 5 :
                    temp = random.randint(1, 100)
                    if temp <= 55 :
                        post = post + "OUT : CF catch"
                    else :
                        post = post + "HIT"
                elif self.hit_direction <= 7 :
                    temp = random.randint(1, 100)
                    if temp <= 55 :
                        post = post + "OUT : RF catch"
                    else :
                        post = post + "HIT"

        elif self.hit_land_pos == 6 :
            judge = judge + "homerun"
            post = post + "homerun"

        print("hit test : ", judge)
        print("post : ", post)

    def hit(self) :
        print("hit")
        self.cnt_throw = self.cnt_throw + 1

        self.cnt_strike = 0
        self.cnt_ball = 0

        self.show_count()

        self.run(1)

    def hit2(self) :
        print("hit2")
        self.cnt_throw = self.cnt_throw + 1

        self.cnt_strike = 0
        self.cnt_ball = 0

        self.show_count()

        self.run(2)

    def hit3(self) :
        print("hit3")
        self.cnt_throw = self.cnt_throw + 1

        self.cnt_strike = 0
        self.cnt_ball = 0

        self.show_count()

        self.run(3)


    def hitHR(self) :
        print("hitHR")
        self.cnt_throw = self.cnt_throw + 1

        self.cnt_strike = 0
        self.cnt_ball = 0

        self.show_count()

        self.run(4)

    
if __name__=="__main__":
    app = QApplication(sys.argv)
    app.setStyle(QStyleFactory.create('Fusion')) # --> 없으면, 헤더색 변경 안됨.
    # print(now, "[MAIN]", sys.argv)
    myWindow = BaseBall()
    myWindow.show()
    app.exec_()
    