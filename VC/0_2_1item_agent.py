import sys
import os
import sqlite3
import time
import math
import pandas as pd
import pyupbit

import datetime
import config
from time import localtime, strftime
from PyQt5.QtWidgets import *
from PyQt5.QAxContainer import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5 import QtTest, QtCore, QtWidgets, uic, QtGui
import module_timer
import module_worker_1_item

form_class = uic.loadUiType("interface.ui")[0]

file = open('../../individual/upas.txt', 'r')
s = file.read()
key = s.split('\n')

TICKERS_1 = config.TICKER_1_ITEM
WORKER_GROUP = len(TICKERS_1)
print("Work G : ", WORKER_GROUP)
NUM_SLOT = len(TICKERS_1)

SUMMARY_TITLES = ['item', 'ask_price', 'bid_price', 'own_count', 'unit_price', 'total_buy', 'percent', 'volume_ratio', 'buy_qty_ratio']
SUMMARY_COL_CNT = len(SUMMARY_TITLES)

class Kiwoom(QMainWindow, form_class):
    def __init__(self):
        global key
        access_key = key[0]
        secret_key = key[1]
        self.upbit = pyupbit.Upbit(access_key, secret_key)

        super().__init__()
        self.setupUi(self)
        if self.init_ENV() == 1 :
            self.start_timer()

    def init_ENV(self) :
        self.list_th_connected = []
        self.worker = []

        for i in range(WORKER_GROUP) :
            self.worker.append(0)
            self.list_th_connected.append(0)

        # ## button 동작 binding
        self.btn_TEST.clicked.connect(self.btn_test)
        self.btn_TEST_2.clicked.connect(self.btn_test_2)

        # ## table setting
        self.func_SET_tableSUMMARY()        # monitoring table
        return 1

    def start_timer(self) :
        self.timer = module_timer.Timer()
        self.timer.cur_time.connect(self.update_times)
        self.timer.cur_balance.connect(self.update_balance)
        self.timer.timer_connected.connect(self.timer_con_finish)
        self.timer.start()

    @pyqtSlot(dict)
    def update_balance(self, data) :
        self.show_cashKRW.setText(str(data['cashKRW']))
        self.show_coinKRW.setText(str(data['coinKRW']))
        self.show_totalKRW.setText(str(data['totalKRW']))

    @pyqtSlot(dict)
    def update_times(self, data) :
        self.show_time.setText(data['time'])
        
    
    @pyqtSlot(int)
    def timer_con_finish(self, data) :
        self.func_start_check()          # Aloha

    def func_start_check(self) :
        self.table_summary.clearContents()      ## table clear
        if self.create_thread() == 0 :              ## thread creation
            print("READY")

    def create_thread(self) :
        for i in range(len(self.worker)) :
            self.th_seq = i
            self.worker[i] = module_worker_1_item.Worker(self.th_seq)
            self.worker[i].th_con.connect(self.th_connected)
            self.worker[i].trans_dict.connect(self.rp_dict)
            self.worker[i].start()

        return 0

    @pyqtSlot(dict)
    def rp_dict(self, data):
        try :
            for i in range(len(SUMMARY_TITLES)) :
                if SUMMARY_TITLES[i] == 'percent' :
                    if data['percent'] > 0 :
                        color = 1
                    elif data['percent'] < 0 :
                        color = 2
                    elif data['percent'] == 0 :
                        color = 0
                    self.func_SET_TableData(1, data['seq'], i, str(data[SUMMARY_TITLES[i]]), color)
                else :
                    self.func_SET_TableData(1, data['seq'], i, str(data[SUMMARY_TITLES[i]]), 0)
        except :
            pass

    def show_cmd(self, group) :
        os.system('cls')
        print("GROUP : ", group)
        print("[GROUP 1]")

    def func_SET_TableData(self, table_no, row, col, content, color):
        item = QTableWidgetItem(content)
        item.setTextAlignment(4)    # 가운데 정렬
        if color == 1:
            item.setForeground(QBrush(Qt.red)) # 글자색
        elif color == 2:
            item.setForeground(QBrush(Qt.blue)) # 글자색

        # summary table
        if table_no == 1:
            self.table_summary.setItem(row, col, item)

    @pyqtSlot(int)
    def th_connected(self, data) :
        self.list_th_connected[self.th_seq] = data
        if 0 not in self.list_th_connected :
            print(self.now(), "[MAIN] [th_connected] Thread Connect Complete")

    def btn_test(self) :
        print("[MAIN] btn test !!!!")
        self.worker.buy_by_manual()
    def btn_test_2(self):
        print("btn test 2")
        self.worker.sell_by_manual()


    def func_SET_tableSUMMARY(self):
        ## Workers #1
        self.table_summary.setRowCount(NUM_SLOT)
        self.table_summary.setColumnCount(SUMMARY_COL_CNT)
        self.table_summary.resizeRowsToContents()

        for i in range(SUMMARY_COL_CNT):
            self.table_summary.setColumnWidth(i, 110)
        
        self.table_summary.verticalHeader().setVisible(False)
        self.table_summary.verticalHeader().setDefaultSectionSize(1)

        for i in range(len(SUMMARY_TITLES)) :
            self.table_summary.setHorizontalHeaderItem(i, QTableWidgetItem(SUMMARY_TITLES[i]))
        
        # self.table_summary.setHorizontalHeaderItem(7, QTableWidgetItem("SELL"))

        # self.table_summary.clicked.connect(lambda: self.sellItem(1))
        self.table_summary.clicked.connect(self.sell_click)
        
    def sell_click(self, clicked):
        row = clicked.row()
        target_item = self.table_summary.item(row, 0).text()
        self.sellItem(target_item)
    def sell_click_2(self, clicked):
        row = clicked.row()
        target_item = self.table_summary_2.item(row, 0).text()
        self.sellItem(target_item)
    def sell_click_3(self, clicked):
        row = clicked.row()
        target_item = self.table_summary_3.item(row, 0).text()
        self.sellItem(target_item)
    def sellItem(self, target_item) :
        orderbook = pyupbit.get_orderbook(target_item)
        bids_asks = orderbook[0]['orderbook_units']
        ask_price = bids_asks[0]['ask_price']
        bid_price = bids_asks[0]['bid_price']

        acc_bal = self.upbit.get_balances()

        try :
            for i in range(0, len(acc_bal[0]), 1) :
                item = acc_bal[0][i]['currency']
                if item != "KRW" and item in target_item :
                    count = acc_bal[0][i]['balance']
                    unit_price = acc_bal[0][i]['avg_buy_price']

                    print("count : ", count, "unit_price : ", unit_price, float(count)*float(unit_price))

            ret = self.upbit.sell_limit_order(target_item, bid_price, count)
            print("[sell Manual] item : ", target_item, "/ price : ", bid_price, "/ Qty : ", qty)
            # print(ret)
        except :
            pass

    def now(self) :
        return datetime.datetime.now()
if __name__=="__main__":
    app = QApplication(sys.argv)
    app.setStyle(QStyleFactory.create('Fusion')) # --> 없으면, 헤더색 변경 안됨.
    # print(now, "[MAIN]", sys.argv)
    myWindow = Kiwoom()
    myWindow.show()
    app.exec_()
    