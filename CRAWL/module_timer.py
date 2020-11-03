import sys
import time
import math
import datetime
import config
from PyQt5.QtCore import *
from PyQt5 import QtTest, QtCore, QtWidgets
import pandas as pd 
import threading
from PyQt5.QtWidgets import *
from PyQt5.QAxContainer import *

class Timer(QThread):
    cur_time = pyqtSignal(dict)
    check_time = pyqtSignal(dict)

    def __init__(self):
        super().__init__()

    def run(self):
        temp_time = {}
        while True:
            now = datetime.datetime.now()

            c_hour = now.strftime('%H')
            c_min = now.strftime('%M')
            c_sec = now.strftime('%S')
            str_time = c_hour + ':' + c_min + ':' + c_sec
            temp_time['time'] = str_time

            # if c_sec == "00" or c_sec == "20" or c_sec == "40" :

            # if c_sec == "00" or c_sec == "30" :
            if c_sec == "00" :
                self.check_time.emit(temp_time)

            self.cur_time.emit(temp_time)
            time.sleep(1)