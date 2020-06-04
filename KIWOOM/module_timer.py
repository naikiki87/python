import sys
import time
import pandas as pd

from PyQt5.QtWidgets import *
from PyQt5.QAxContainer import *
from PyQt5.QtGui import *
# from PyQt5.QtCore import QThread, QObject, pyqtSignal
from PyQt5.QtCore import *
from PyQt5 import QtTest, QtCore

class Timer(QThread):
    finished = pyqtSignal(str)

    def run(self):
        cnt = 0
        while True:
            if cnt > 5 :
                date = QDateTime.currentDateTime().toString("hh:mm:ss")
                self.finished.emit(date)
            cnt = cnt + 1
            time.sleep(1)