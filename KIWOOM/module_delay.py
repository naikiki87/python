import sys
import time
import config
from PyQt5.QtCore import *
from PyQt5 import QtTest, QtCore, QtWidgets
import threading

class Delay(QThread):
    candidate = pyqtSignal(dict)
    resume = pyqtSignal(int)

    def run(self):
        print("delay triggered")
        QtTest.QTest.qWait(30000)
        self.resume.emit(1)