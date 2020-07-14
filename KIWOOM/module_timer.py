import sys
import time
import datetime
from PyQt5.QtCore import *
from PyQt5 import QtTest, QtCore, QtWidgets

class Timer(QThread):
    cur_time = pyqtSignal(dict)

    def run(self):
        temp_time = {}
        while True:
            now = datetime.datetime.now()
            mkt_open = now.replace(hour=9, minute=0, second=0)
            mkt_close = now.replace(hour=15, minute=20, second=0)

            c_hour = now.strftime('%H')
            c_min = now.strftime('%M')
            c_sec = now.strftime('%S')

            str_time = c_hour + ':' + c_min + ':' + c_sec
            temp_time['time'] = str_time

            if now >= mkt_open and now < mkt_close :
                temp_time['possible'] = 1
            else :
                temp_time['possible'] = 0
            self.cur_time.emit(temp_time)
            time.sleep(1)