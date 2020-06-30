import sys
import time
from PyQt5.QtCore import *
from PyQt5 import QtTest, QtCore, QtWidgets

class Timer(QThread):
    cur_time = pyqtSignal(str)

    def run(self):
        while True:
            date = QDateTime.currentDateTime().toString("hh:mm:ss")
            self.cur_time.emit(date)
            time.sleep(1)

    def start_test(self):
        self.index = 0
        while True:
            print(self.index)
            self.index = self.index + 1
            QtTest.QTest.qWait(3000)
