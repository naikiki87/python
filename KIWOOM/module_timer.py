import sys
import time
from PyQt5.QtCore import *

class Timer(QThread):
    cur_time = pyqtSignal(str)

    def run(self):
        while True:
            date = QDateTime.currentDateTime().toString("hh:mm:ss")
            self.cur_time.emit(date)
            time.sleep(1)