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
import module_worker_1
import module_worker_2
import module_worker_3

form_class = uic.loadUiType("interface.ui")[0]

file = open('../../individual/upas.txt', 'r')
s = file.read()
key = s.split('\n')

TICKERS_1 = config.TICKERS_1
TICKERS_2 = config.TICKERS_2
TICKERS_3 = config.TICKERS_3

WORKER_GROUP = 5

NUM_SLOT = config.NUM_SLOT
SUMMARY_COL_CNT = config.SUMMARY_COL_CNT

SUMMARY_TITLES = ['item', 'ask_price', 'bid_price', 'own_count', 'unit_price', 'percent', 'wave']

class Kiwoom(QMainWindow, form_class):
    def __init__(self):
        global key
        access_key = key[0]
        secret_key = key[1]
        self.upbit = pyupbit.Upbit(access_key, secret_key)

        super().__init__()
        self.setupUi(self)
        self.set_db_table()
        if self.init_ENV() == 1 :
            self.start_timer()

    def init_ENV(self) :
        self.status_1 = pd.DataFrame(columns = ['item', 'ask_price', 'bid_price', 'own_count', 'unit_price', 'percent', 'wave'])
        self.status_2 = pd.DataFrame(columns = ['item', 'ask_price', 'bid_price', 'own_count', 'unit_price', 'percent', 'wave'])
        self.status_3 = pd.DataFrame(columns = ['item', 'ask_price', 'bid_price', 'own_count', 'unit_price', 'percent', 'wave'])

        self.list_th_connected = []
        self.list_th_connected_2 = []
        self.list_th_connected_3 = []

        self.renew_1 = []
        self.renew_2 = []
        self.renew_3 = []

        for i in range(WORKER_GROUP) :
            self.renew_1.append(0)
            self.renew_2.append(0)
            self.renew_3.append(0)

            self.list_th_connected.append(0)
            self.list_th_connected_2.append(0)
            self.list_th_connected_3.append(0)

        ## 1군
        self.workers_1 = list(range(0, WORKER_GROUP))
        ## 2군
        self.workers_2 = list(range(0, WORKER_GROUP))
        ## 3군
        self.workers_3 = list(range(0, WORKER_GROUP))

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
        print(";fnc start check")
        self.table_summary.clearContents()      ## table clear
        if self.create_thread() == 0 :              ## thread creation
            print("create thread complete")

    def create_thread(self) :
        for i in range(len(self.workers_1)) :
            self.th_seq = i
            self.workers_1[i] = module_worker_1.Worker(self.th_seq)
            self.workers_1[i].th_con.connect(self.th_connected)
            self.workers_1[i].trans_dict.connect(self.rp_dict)
            self.workers_1[i].start()

        for i in range(len(self.workers_2)) :
            self.th_seq = i
            self.workers_2[i] = module_worker_2.Worker(self.th_seq)
            self.workers_2[i].th_con.connect(self.th_connected)
            self.workers_2[i].trans_dict.connect(self.rp_dict_2)
            self.workers_2[i].start()

        for i in range(len(self.workers_3)) :
            self.th_seq = i
            self.workers_3[i] = module_worker_3.Worker(self.th_seq)
            self.workers_3[i].th_con.connect(self.th_connected)
            self.workers_3[i].trans_dict.connect(self.rp_dict_3)
            self.workers_3[i].start()

        return 0

    @pyqtSlot(dict)
    def rp_dict_3(self, data):
        try :
            self.status_3.loc[data['seq']] = [data['item'], data['ask_price'], data['bid_price'], data['own_count'], data['unit_price'], data['percent'], data['wave']]
            self.renew_3[data['seq']] = 1

            if sum(self.renew_3) == 5 :
                self.renew_3 = []
                for i in range(WORKER_GROUP) :
                    self.renew_3.append(0)

                self.status_3 = self.status_3.sort_index()
                # self.show_cmd(3)

            for i in range(len(SUMMARY_TITLES)) :
                if SUMMARY_TITLES[i] == 'percent' :
                    if data['percent'] > 0 :
                        color = 1
                    elif data['percent'] < 0 :
                        color = 2
                    elif data['percent'] == 0 :
                        color = 0
                    self.func_SET_TableData(3, data['seq'], i, str(data[SUMMARY_TITLES[i]]), color)
                else :
                    self.func_SET_TableData(3, data['seq'], i, str(data[SUMMARY_TITLES[i]]), 0)

        except :
            pass

    @pyqtSlot(dict)
    def rp_dict_2(self, data):
        try :
            self.status_2.loc[data['seq']] = [data['item'], data['ask_price'], data['bid_price'], data['own_count'], data['unit_price'], data['percent'], data['wave']]
            self.renew_2[data['seq']] = 1

            if sum(self.renew_2) == 5 :
                self.renew_2 = []
                for i in range(WORKER_GROUP) :
                    self.renew_2.append(0)

                self.status_2 = self.status_2.sort_index()
                # self.show_cmd(2)

            for i in range(len(SUMMARY_TITLES)) :
                if SUMMARY_TITLES[i] == 'percent' :
                    if data['percent'] > 0 :
                        color = 1
                    elif data['percent'] < 0 :
                        color = 2
                    elif data['percent'] == 0 :
                        color = 0
                    self.func_SET_TableData(2, data['seq'], i, str(data[SUMMARY_TITLES[i]]), color)
                else :
                    self.func_SET_TableData(2, data['seq'], i, str(data[SUMMARY_TITLES[i]]), 0)

        except :
            pass
        
    @pyqtSlot(dict)
    def rp_dict(self, data):
        try :
            self.status_1.loc[data['seq']] = [data['item'], data['ask_price'], data['bid_price'], data['own_count'], data['unit_price'], data['percent'], data['wave']]
            self.renew_1[data['seq']] = 1

            if sum(self.renew_1) == 5 :
                self.renew_1 = []
                for i in range(WORKER_GROUP) :
                    self.renew_1.append(0)

                self.status_1 = self.status_1.sort_index()
                # self.show_cmd(1)

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
        print(self.status_1)
        print("[GROUP 2]")
        print(self.status_2)
        print("[GROUP 3]")
        print(self.status_3)

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
        if table_no == 2:
            self.table_summary_2.setItem(row, col, item)
        if table_no == 3:
            self.table_summary_3.setItem(row, col, item)
        # history table
        # if table_no == 2:
        #     self.table_history.setItem(row, col, item)
        # order table
        # if table_no == 3:
        #     self.table_order.setItem(row, col, item)
        if table_no == 4:
            self.table_dailyprofit.setItem(row, col, item)

    @pyqtSlot(int)
    def th_connected(self, data) :
        self.list_th_connected[self.th_seq] = data
        if 0 not in self.list_th_connected :
            print(self.now(), "[MAIN] [th_connected] Thread Connect Complete")

    def btn_test(self) :
        print("[MAIN] btn test !!!!")
    def btn_test_2(self):
        print("btn test 2")

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
        
        self.table_summary.setHorizontalHeaderItem(7, QTableWidgetItem("SELL"))

        # self.table_summary.clicked.connect(lambda: self.sellItem(1))
        self.table_summary.clicked.connect(self.sell_click)
        
        ## Workers #2
        self.table_summary_2.setRowCount(NUM_SLOT)
        self.table_summary_2.setColumnCount(SUMMARY_COL_CNT)
        self.table_summary_2.resizeRowsToContents()

        for i in range(SUMMARY_COL_CNT):
            self.table_summary_2.setColumnWidth(i, 110)
        
        self.table_summary_2.verticalHeader().setVisible(False)
        self.table_summary_2.verticalHeader().setDefaultSectionSize(1)

        for i in range(len(SUMMARY_TITLES)) :
            self.table_summary_2.setHorizontalHeaderItem(i, QTableWidgetItem(SUMMARY_TITLES[i]))

        self.table_summary_2.setHorizontalHeaderItem(7, QTableWidgetItem("SELL"))
        self.table_summary_2.clicked.connect(self.sell_click_2)

        ## Workers #3
        self.table_summary_3.setRowCount(NUM_SLOT)
        self.table_summary_3.setColumnCount(SUMMARY_COL_CNT)
        self.table_summary_3.resizeRowsToContents()

        for i in range(SUMMARY_COL_CNT):
            self.table_summary_3.setColumnWidth(i, 110)
        
        self.table_summary_3.verticalHeader().setVisible(False)
        self.table_summary_3.verticalHeader().setDefaultSectionSize(1)

        for i in range(len(SUMMARY_TITLES)) :
            self.table_summary_3.setHorizontalHeaderItem(i, QTableWidgetItem(SUMMARY_TITLES[i]))

        self.table_summary_3.setHorizontalHeaderItem(7, QTableWidgetItem("SELL"))
        self.table_summary_3.clicked.connect(self.sell_click_3)

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
        print("sellIOtem : ", target_item)
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
            print(ret)
        except :
            pass
    
    def set_db_table(self) :
        conn = sqlite3.connect("item_status.db")
        cur = conn.cursor()
        sql = "create table if not exists STATUS (item text primary_key, step integer)"
        cur.execute(sql)
        conn.commit()

        sql = "insert into STATUS(item, step) select :ITEM, :STEP where not exists (select * from STATUS where item=:ITEM)"
        for i in range(len(TICKERS_1)) :
            item = TICKERS_1[i]
            step = 0
            cur.execute(sql, {"ITEM" : item, "STEP" : step})

        for i in range(len(TICKERS_2)) :
            item = TICKERS_2[i]
            step = 0
            cur.execute(sql, {"ITEM" : item, "STEP" : step})

        for i in range(len(TICKERS_3)) :
            item = TICKERS_3[i]
            step = 0
            cur.execute(sql, {"ITEM" : item, "STEP" : step})

        conn.commit()
        conn.close()

    def now(self) :
        return datetime.datetime.now()
if __name__=="__main__":
    app = QApplication(sys.argv)
    app.setStyle(QStyleFactory.create('Fusion')) # --> 없으면, 헤더색 변경 안됨.
    # print(now, "[MAIN]", sys.argv)
    myWindow = Kiwoom()
    myWindow.show()
    app.exec_()
    