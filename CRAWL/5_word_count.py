import collections
import requests
from bs4 import BeautifulSoup
import io
import pandas as pd
import re
import config
import schedule
import datetime
import sys
import sqlite3
import time
import math
import pandas as pd
import threading
# import datetime
# import config
from time import localtime, strftime
from PyQt5.QtWidgets import *
from PyQt5.QAxContainer import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5 import QtTest, QtCore, QtWidgets, uic, QtGui

import module_timer

EXCEPT = config.EXCEPT
NUM_PAGE = config.NUM_PAGE

# pd.set_option('display.max_row', 20000)
# pd.set_option('display.max_columns', 10000)
pd.set_option('display.max_rows', None)
pd.set_option('display.max_columns', None)
pd.set_option('display.width', None)
pd.set_option('display.max_colwidth', -1)

form_class = uic.loadUiType("interface.ui")[0]

check = True

class real_keyword(QMainWindow, form_class):
    test_dict0 = pyqtSignal(dict)

    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.setWindowTitle("pyqt")
        # self.init_ENV()
        self.timer = module_timer.Timer()
        self.timer.cur_time.connect(self.cur_time)
        self.timer.check_time.connect(self.check_time)
        self.timer.start()

    def init_ENV(self) :
        self.btn_TEST.clicked.connect(self.start_real)
        self.btn_TEST2.clicked.connect(self.stop_real)

    @pyqtSlot(dict)
    def check_time(self, data) :
        global check
        self.show_time.setText(str(data['time']))

        if check :
            self.job(data)

    @pyqtSlot(dict)
    def cur_time(self, data) :
        global check

    

    def stop_real(self) :
        global check
        check = False
    
    def start_real(self) :
        global check
        check = True

    def job(self, data) :
        print("job start")
        text_list = []
        for i in range(NUM_PAGE):
            page = i * 30 + 1
            url = "http://mlbpark.donga.com/mp/b.php?p={page}&b=bullpen&id=202006130043772831&select=&query=&user=&site=donga.com&reply=&source=&sig=h6jRHl-gkh9RKfX2hgj9Sf-ghhlq".format(page = page)
            res = requests.get(url)
            soup = BeautifulSoup(res.content, 'lxml')

            topic = soup.findAll("span", class_="word_bullpen")
            title = soup.findAll("span", {"class" : "bullpen"})
            count = soup.findAll("span", {"class" : "viewV"})

            for j in range(len(title)):
                title_text = title[j].text.strip()

                words = title_text.split(' ')
                if words[0] == '' :
                    a = 1
                else :
                    for j in range(len(words)) :
                        words[j] = words[j].strip()         # 공백 제거
                        print("대상 : ", words[j])

                        if words[j] in EXCEPT : 
                            print("in except 1 : ", words[j])
                            continue
                        elif words[j] != '' :
                            len_word = len(words[j])
                            if words[j][len_word-1] == "은" or words[j][len_word-1] == "는" or words[j][len_word-1] == "이" or words[j][len_word-1] == "가":
                                words[j] = words[j][0:len_word-1]

                            if words[j] in EXCEPT :
                                print("in except 2 : ", words[j])
                                continue
                            else :
                                print("world : ", words[j])
                                words[j] = re.sub('[0-9]+', '', words[j])
                                words[j] = re.sub('[A-Za-z]+', '', words[j])
                                words[j] = re.sub('[-=+,#/\?:^$.@*\"※~&%ㆍ·!』\\‘’|\(\)\[\]\<\>`\'…》]', '', words[j])
                                text_list.append(words[j])

        word_list = pd.Series(text_list)

        now = datetime.datetime.now()
        c_hour = now.strftime('%H')
        c_min = now.strftime('%M')
        c_sec = now.strftime('%S')
        str_time = c_hour + ':' + c_min + ':' + c_sec

        # print("time : ", str_time)
        # print(word_list.value_counts().head(20))

        self.show_rank.setText(str(word_list.value_counts().head(20)))

    
if __name__=="__main__":
    app = QApplication(sys.argv)
    app.setStyle(QStyleFactory.create('Fusion')) # --> 없으면, 헤더색 변경 안됨.
    myWindow = real_keyword()
    myWindow.show()
    app.exec_()
    