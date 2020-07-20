import sys
import time
import datetime
from PyQt5.QtCore import *
from PyQt5 import QtTest, QtCore, QtWidgets
import module_item_finder

class Timer(QThread):
    cur_time = pyqtSignal(dict)
    new_deal = pyqtSignal(dict)

    def run(self):
        temp_time = {}
        worker = module_item_finder.ItemFinder()
        test_time = 0
        # worker.run()
        while True:
            if test_time == 5 :
                new_deal = {}
                new_deal['item_code'] = "035720"
                new_deal['qty'] = 2
                self.new_deal.emit(new_deal)

            now = datetime.datetime.now()
            mkt_open = now.replace(hour=9, minute=0, second=0)
            mkt_close = now.replace(hour=15, minute=20, second=0)
            item_finding = now.replace(hour=13, minute=53, second=30)
            # item_finding = now.replace(hour=13, minute=52, second=0)

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
            print("Test Time : ", test_time)
            test_time = test_time + 1

            time.sleep(1)
            if now == item_finding :
                worker.finder_test()

            # worker.finder_test()