import sys
import time
import datetime
import pandas as pd
import numpy as np
import sqlite3
import math
from time import localtime, strftime
from PyQt5.QtWidgets import *
from PyQt5.QAxContainer import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5 import QtTest, QtCore
from collections import deque
import config

ACCOUNT = config.ACCOUNT
PASSWORD = config.PASSWORD
TAX = config.TAX
FEE_BUY = config.FEE_BUY
FEE_SELL = config.FEE_SELL
GOAL_PER = config.GOAL_PER
MAKE_ORDER = config.MAKE_ORDER
PER_LOW = config.PER_LOW
STEP_LIMIT = config.STEP_LIMIT
DOWN_DURATION = config.DOWN_DURATION
JUDGE_SHOW = 0
TEST_CODE = 1

ADD_PRICE = config.ADD_PRICE
ADD_PRICE_1 = config.ADD_PRICE_1
ADD_PRICE_2 = config.ADD_PRICE_2
AUTO_BUY_PRICE_LIM = config.AUTO_BUY_PRICE_LIM
TARGET_PER = 2

PER_LOW_0 = config.PER_LOW_0
PER_LOW_1 = config.PER_LOW_1


print("TARGET PERCENT : ", TARGET_PER)
print("AUTO BUY PRICE : ", AUTO_BUY_PRICE_LIM)
print("ADD PRICE : ", ADD_PRICE_1, ADD_PRICE_2)
# print("ADD PRICE : ", ADD_PRICE)

class Worker(QThread):
    connected = 0
    trans_dict = pyqtSignal(dict)
    th_con = pyqtSignal(int)
    rq_order = pyqtSignal(dict)
    first_jumun_check = pyqtSignal(dict)

    def __init__(self, seq):
        super().__init__()
        self.item_code = ''
        self.seq = seq
        self.items = deque()
        self.first_rcv = 1

        self.step = 0
        self.per_low = 0
        self.add_water = 0

        self.uping = 0
        self.up_level = 0
        self.up_maginot = -2
        self.up_hook_per = 0

        self.downing = 0
        self.down_level = 0
        self.down_maginot = -2
        self.down_hook_per = 0

    def event_connect(self, err_code):
        if err_code == 0:
            self.connected = 1
        else:
            print(self.now(), "[ TH", self.seq, "] [event_connect] thread disconnected")

    def run(self):
        self.lock = 0       ## lock variable initialize
        self.cnt = 0
        self.th_con.emit(1)

    @pyqtSlot(dict)
    def che_result(self, data) :
        if data['th_num'] == self.seq :
            print(self.now(), "[ TH", self.seq, "] [che_result] Chejan Data Received")

            item_code = data['item_code']
            orderType = self.func_GET_db_item(item_code, 3)
            res = data['res']

            if orderType != "none" :
                ## Add water
                if orderType == 1 :
                    cur_step = self.func_GET_db_item(item_code, 1)          ## DB : step -> cur_step
                    self.step = cur_step + 1
                    if self.func_UPDATE_db_item(item_code, 1, self.step) == 1 :   ## update step
                        if self.func_UPDATE_db_item(item_code, 2, 0) == 1:       ## ordered -> 0
                            if self.func_UPDATE_db_item(item_code, 3, 0) == 1:       ## orderType -> 0
                                self.downing = 0
                                self.down_level = 0
                                self.down_maginot = -2
                                self.down_hook_per = 0
                                self.add_water = 1
                                self.lock = 0

                ## full sell
                elif orderType == 3 :
                    self.func_DELETE_db_item(item_code)     ## DB : DELETE Item
                    self.uping = 0
                    self.up_level = 0
                    self.up_maginot = -2
                    self.up_hook_per = 0

                    self.step = 0
                    self.lock = 0           ## unlock

                ## new BUY(Manual)
                elif orderType == 5 :
                    if self.func_UPDATE_db_item(item_code, 2, 0) == 1:       ## ordered -> 0
                        if self.func_UPDATE_db_item(item_code, 3, 0) == 1:       ## orderType -> 0
                            self.lock = 0           ## unlock

                ## gi BUY(Manual)
                elif orderType == 6 :
                    if self.func_UPDATE_db_item(item_code, 2, 0) == 1:       ## ordered -> 0
                        if self.func_UPDATE_db_item(item_code, 3, 0) == 1:       ## orderType -> 0
                            self.lock = 0           ## unlock

                ## partial SELL(Manual)
                elif orderType == 7 :
                    if self.func_UPDATE_db_item(item_code, 2, 0) == 1:       ## ordered -> 0
                        if self.func_UPDATE_db_item(item_code, 3, 0) == 1:       ## orderType -> 0
                            self.lock = 0           ## unlock

                ## FULL SELL(Manual)
                elif orderType == 8 :
                    self.func_DELETE_db_item(item_code)     ## DB : DELETE Item
                    self.lock = 0           ## unlock

                ## new BUY(item finder)
                elif orderType == 9 :
                    if self.func_UPDATE_db_item(item_code, 2, 0) == 1:       ## ordered -> 0
                        if self.func_UPDATE_db_item(item_code, 3, 0) == 1:       ## orderType -> 0
                            self.lock = 0           ## unlock

    @pyqtSlot(int)
    def resume_paused(self, data) :
        if data == self.seq : 
            print("worker", self.seq, "resume paused")
            item_code = self.item_code
            orderType = self.func_GET_db_item(item_code, 3)
            if orderType != "none" :                ## after get data from db
                if orderType == 1 :                                             ## add water
                    if self.func_UPDATE_db_item(item_code, 2, 0) == 1:       ## ordered -> 0
                        # self.indicate_release()
                        self.lock = 0                           ## unlock

                elif orderType == 5 :                           # 신규 buy인 경우 db삭제 및 lock 해제
                    self.func_DELETE_db_item(item_code)         ## DB : DELETE Item
                    self.lock = 0                               ## unlock

                elif orderType == 9 :                           # 신규 item finding buy인 경우 db삭제 및 lock 해제
                    self.func_DELETE_db_item(item_code)         ## DB : DELETE Item
                    self.lock = 0                               ## unlock

                else :                                          # 다른 sit인 경우 db order 정보 0으로 세팅 및 lock 해제
                    if self.func_UPDATE_db_item(item_code, 2, 0) == 1:       ## ordered -> 0
                        self.lock = 0                           ## unlock

    @pyqtSlot(dict)
    def reply_first_check(self, data) :
        if data['slot'] == self.seq :
            item_code = data['item_code']
            if self.func_UPDATE_db_item(item_code, 2, 0) == 1:          ## ordered -> 0
                self.first_rcv = 0
                self.lock = 0

    @pyqtSlot(dict)
    def dict_from_main(self, data) :
        if self.lock == 1 :
            print("worker : ", self.seq, "lock : ", self.lock)
        item_code = data['item_code']
        self.item_code = item_code
        # deposit = data['deposit']

        if data['autoTrade'] == 0 :                                             ## manual trading 시
            self.lock = 1
            orderType = data['orderType']
            print("worker", self.seq, 'ordertype : ', orderType)
            if orderType == 5 :                                                 ## 신규 item manual 매수
                if MAKE_ORDER == 1 :
                    qty = data['qty']
                    price = data['price']

                    self.func_INSERT_db_item(item_code, 0, 0, 0, -1)             ## 신규 item db insert

                    if self.func_UPDATE_db_item(item_code, 2, 1) == 1:          ## ordered -> 1
                        if self.func_UPDATE_db_item(item_code, 3, 5) == 1:       ## orderType -> 5(manual buy)
                            order = {}
                            order['slot'] = self.seq
                            order['type'] = 0       ## buy
                            order['item_code'] = item_code
                            order['qty'] = qty
                            order['price'] = price
                            order['order_type'] = orderType
                            self.rq_order.emit(order)

            elif orderType == 9 :         ## 신규 item finding 매수
                if MAKE_ORDER == 1 :
                    qty = data['qty']
                    price = data['price']

                    self.func_INSERT_db_item(item_code, 0, 0, 0, -1)     ## 신규 item db insert

                    if self.func_UPDATE_db_item(item_code, 2, 1) == 1:       ## ordered -> 1
                        if self.func_UPDATE_db_item(item_code, 3, 9) == 1:       ## orderType -> 9(manual item finding buy)
                            order = {}
                            order['slot'] = self.seq
                            order['type'] = 0       ## buy
                            order['item_code'] = item_code
                            order['qty'] = qty
                            order['price'] = price
                            order['order_type'] = orderType
                            self.rq_order.emit(order)

                            # print(self.now(), "[ TH", self.seq, "] [dict_from_main] New Buy Item Finding : ", item_code)

            elif orderType == 6 :       ## 기존 item 수동 매수
                if MAKE_ORDER == 1 :
                    qty = data['qty']
                    price = data['price']

                    if self.func_UPDATE_db_item(item_code, 2, 1) == 1:       ## ordered -> 1
                        if self.func_UPDATE_db_item(item_code, 3, 6) == 1:       ## orderType -> 6(manual gi buy)
                            order = {}
                            order['slot'] = self.seq
                            order['type'] = 0       ## buy
                            order['item_code'] = item_code
                            order['qty'] = qty
                            order['price'] = price
                            order['order_type'] = orderType
                            self.indicate_ordered()         ## INDICATE : ordered
                            self.rq_order.emit(order)

                            # print(self.now(), "[ TH", self.seq, "] [dict_from_main] Gi Buy Manual : ", item_code)

            elif orderType == 7 :       ## 일부 sell manual
                if MAKE_ORDER == 1 :
                    qty = data['qty']
                    price = data['price']

                    if self.func_UPDATE_db_item(item_code, 2, 1) == 1:      ## ordered 변경 -> 1
                        if self.func_UPDATE_db_item(item_code, 3, 7) == 1:  ## orderType 변경 -> 7(manual sell)
                            order = {}
                            order['slot'] = self.seq
                            order['type'] = 1       ## sell
                            order['item_code'] = item_code
                            order['qty'] = qty
                            order['price'] = price
                            order['order_type'] = orderType
                            self.indicate_ordered()         ## INDICATE : ordered
                            self.rq_order.emit(order)

                            # print(self.now(), "[ TH", self.seq, "] [dict_from_main] Part Sell Manual : ", item_code)
                            
            elif orderType == 8 :       ## full sell manu al
                if MAKE_ORDER == 1 :
                    qty = data['qty']
                    price = data['price']

                    if self.func_UPDATE_db_item(item_code, 2, 1) == 1:      ## ordered 변경 -> 1
                        if self.func_UPDATE_db_item(item_code, 3, 8) == 1:  ## orderType 변경 -> 8(manual sell full)
                            order = {}
                            order['slot'] = self.seq
                            order['type'] = 1      ## sell
                            order['item_code'] = item_code
                            order['qty'] = qty
                            order['price'] = price
                            order['order_type'] = orderType
                            self.indicate_ordered()         ## INDICATE : ordered
                            self.rq_order.emit(order)

                            # print(self.now(), "[ TH", self.seq, "] [dict_from_main] Full Sell Manual : ", item_code)

        elif data['autoTrade'] == 1 :                   ## auto trading 시
            own_count = data['own_count']
            unit_price = data['unit_price']
            price_buy = data['price_buy']
            price_sell = data['price_sell']

            t_purchase = own_count * unit_price
            t_evaluation = own_count * price_buy    ## 매수 최우선가 기준
            temp_total = t_evaluation - t_purchase
            fee_buy = int(((FEE_BUY * t_purchase) // 10) * 10)
            fee_sell = int(((FEE_SELL * t_evaluation) // 10) * 10)
            tax = int(TAX * t_evaluation)
            total_fee = fee_buy + fee_sell + tax
            total_sum = t_evaluation - t_purchase - total_fee
            percent = round((total_sum / t_purchase) * 100, 2)

            if self.add_water == 1 :
                self.per_low = round((percent - 1), 2)
                if self.func_UPDATE_db_item(item_code, 4, self.per_low) == 1:      ## 현재 perlow 저장
                    self.add_water = 0

            self.rp_dict = {}
            self.rp_dict.update(data)
            self.rp_dict['ordered'] = 0
            self.rp_dict['t_purchase'] = int(t_purchase)
            self.rp_dict['t_evaluation'] = int(t_evaluation)
            self.rp_dict['temp_total'] = int(temp_total)
            self.rp_dict['total_fee'] = int(total_fee)
            self.rp_dict['total_sum'] = int(total_sum)
            self.rp_dict['percent'] = percent
            self.rp_dict['step'] = self.step
            self.rp_dict['seq'] = self.seq
            self.rp_dict['vol_sell'] = data['volume_sell']
            self.rp_dict['vol_buy'] = data['volume_buy']
            self.rp_dict['vol_ratio'] = data['volume_ratio']

            self.trans_dict.emit(self.rp_dict)                  ## show data

            if self.first_rcv == 1 :
                self.step = self.func_GET_db_item(item_code, 1)
                self.per_low = self.func_GET_db_item(item_code, 4)

                if self.lock == 0 :
                    self.lock = 1
                    self.first_rcv = 0

                    if self.func_GET_db_item(item_code, 2) == 1 :           ## 프로그램이 시작했는데 현재 item이 order 중인 경우 
                        self.rp_dict = {}
                        self.indicate_ordered()         ## INDICATE : ordered

                        ordered_item = {}
                        ordered_item['slot'] = self.seq
                        ordered_item['item_code'] = item_code
                        self.first_jumun_check.emit(ordered_item)

                    else :
                        # self.first_rcv = 0
                        self.lock = 0

            else :      ## 2번째 receive 부터
                if self.lock == 0 :
                    self.lock = 1       ## lock 체결

                    if self.downing == 0 and self.uping == 0 :
                        if self.step < STEP_LIMIT and percent <= self.per_low :
                            print("worker", self.seq, "down hooked")
                            try :
                                f_hook = open("trade_log.txt",'a')
                                data = self.get_now() + "[HOOKING DOWN] item : " + str(item_code) + ' ' + str(percent) + '\n'
                                f_hook.write(data)
                                f_hook.close()
                            except :
                                pass
                            
                            self.down_hook_per = percent
                            self.down_level = 0
                            self.down_maginot = -2
                            self.downing = 1
                            self.lock = 0

                        elif percent >= TARGET_PER :
                            print("worker", self.seq, "up hooked")
                            try :
                                f_hook = open("trade_log.txt",'a')
                                data = self.get_now() + "[HOOKING UP] item : " + str(item_code) + ' ' + str(percent) + '\n'
                                f_hook.write(data)
                                f_hook.close()
                            except :
                                pass

                            self.up_hook_per = percent
                            self.up_level = 0
                            self.up_maginot = -2
                            self.uping = 1
                            self.lock = 0

                        else :
                            self.lock = 0

                    elif self.uping == 1 :
                        if percent == self.up_hook_per :
                            print(self.seq, "UP LEVEL : ", self.up_level, '/', self.up_maginot)
                            self.lock = 0
                        
                        elif percent > self.up_hook_per :
                            self.up_hook_per = percent           ## 기준 값 갱신
                            self.up_level = self.up_level + 1
                            self.up_maginot = self.up_level - 2
                            print(self.seq, "UP LEVEL : ", self.up_level, '/', self.up_maginot)
                            self.lock = 0

                        elif percent < self.up_hook_per :
                            self.up_hook_per = percent           ## 기준 값 갱신
                            self.up_level = self.up_level - 1
                            print(self.seq, "UP LEVEL : ", self.up_level, '/', self.up_maginot)

                            if self.up_level == self.up_maginot :
                                # price = int(price_buy)
                                # qty = own_count
                                if MAKE_ORDER == 1 :
                                    if self.func_UPDATE_db_item(item_code, 2, 1) == 1:      ## ordered 변경 -> 1
                                        if self.func_UPDATE_db_item(item_code, 3, 3) == 1:  ## orderType 변경 -> 3

                                            try :
                                                f_hook = open("trade_log.txt",'a')
                                                data = self.get_now() + "[HOOK & SELL] item : " + str(item_code) + ' ' + str(percent) + '\n'
                                                f_hook.write(data)
                                                f_hook.close()
                                            except :
                                                pass

                                            order = {}
                                            order['slot'] = self.seq
                                            order['type'] = 1       ## sell
                                            order['item_code'] = item_code
                                            order['qty'] = own_count       ## 전량
                                            order['price'] = int(price_buy)   ## 매수 최우선가
                                            order['order_type'] = 3
                                            # self.indicate_ordered()         ## INDICATE : ordered
                                            self.rq_order.emit(order)       ## make order to master
                            else :
                                self.lock = 0

                    elif self.downing == 1 :
                        if percent == self.down_hook_per :
                            print(self.seq, "DOWN LEVEL : ", self.down_level, '/', self.down_maginot)
                            self.lock = 0
                        
                        elif percent < self.down_hook_per :
                            self.down_hook_per = percent
                            self.down_level = self.down_level + 1
                            self.down_maginot = self.down_level - 2
                            print(self.seq, "DOWN LEVEL : ", self.down_level, '/', self.down_maginot)
                            self.lock = 0

                        elif percent > self.down_hook_per :
                            self.down_hook_per = percent
                            self.down_level = self.down_level - 1
                            print(self.seq, "DOWN LEVEL : ", self.down_level, '/', self.down_maginot)

                            if self.down_level == self.down_maginot :
                                price = int(price_sell)
                                # qty = math.ceil(ADD_PRICE / price)

                                if self.step == 0 :
                                    qty = math.ceil(ADD_PRICE_1 / price)

                                elif self.step == 1 :
                                    qty = math.ceil(ADD_PRICE_2 / price)


                                if MAKE_ORDER == 1 :
                                    if self.func_UPDATE_db_item(item_code, 2, 1) == 1:       ## ordered -> 1
                                        if self.func_UPDATE_db_item(item_code, 3, 1) == 1:       ## orderType -> 1
                                            try :
                                                f_hook = open("trade_log.txt",'a')
                                                data = self.get_now() + "[HOOK & SELL] item : " + str(item_code) + ' ' + str(percent) + '\n'
                                                f_hook.write(data)
                                                f_hook.close()
                                            except :
                                                pass

                                            order = {}
                                            order['slot'] = self.seq
                                            order['type'] = 0       ## buy
                                            order['item_code'] = item_code
                                            order['qty'] = qty
                                            order['price'] = price
                                            order['order_type'] = 1
                                            # self.indicate_ordered()         ## INDICATE : ordered
                                            self.rq_order.emit(order)       ## make order to master
                            else :
                                self.lock = 0

            
    def func_GET_db_item(self, code, col):
        conn = sqlite3.connect("item_status.db")
        cur = conn.cursor()
        if col == 0:        # get all codes
            sql = "select code from STATUS"
            cur.execute(sql)
            rows = cur.fetchall()
            conn.close()

            if rows is None :
                return "none"
            else:
                codes = []
                for row in rows:
                    codes.append(row[0])
                return codes
        else :
            if col == 1:        # get step
                sql = "select step from STATUS where code = ?"
                cur.execute(sql, [code])
            elif col == 2:      # get ordered
                sql = "select ordered from STATUS where code = ?"
                cur.execute(sql, [code])
            elif col == 3:      # get orderType
                sql = "select orderType from STATUS where code = ?"
                cur.execute(sql, [code])
            elif col == 4:      # get perlow
                sql = "select perlow from STATUS where code = ?"
                cur.execute(sql, [code])

            row = cur.fetchone()
            conn.close()

            if row is None:
                return "none"
            else:
                return row[0]
    
    def func_UPDATE_db_item(self, code, col, data) :
        conn = sqlite3.connect("item_status.db", timeout=10)
        cur = conn.cursor()
        if col == 1:    # update step
            sql = "update STATUS set step = :DATA where code = :CODE"    
            cur.execute(sql, {"DATA" : data, "CODE" : code})
        elif col == 2:  # update ordered
            sql = "update STATUS set ordered = :DATA where code = :CODE"    
            cur.execute(sql, {"DATA" : data, "CODE" : code})
        elif col == 3:  # update orderType
            sql = "update STATUS set orderType = :DATA where code = :CODE"    
            cur.execute(sql, {"DATA" : data, "CODE" : code})
            #### type ####
            # 0 : normai(default)
            # 1 : 물타기
            # 2 : 수익실현 및 복구
            # 3 : full 매도
            # 4 : 존버
        elif col == 4:  # update perlow
            sql = "update STATUS set perlow = :DATA where code = :CODE"    
            cur.execute(sql, {"DATA" : data, "CODE" : code})

        conn.commit()
        conn.close()
        success = cur.rowcount
        # print(now, "[ TH", self.seq, "]", "UPDATED")
        return success
    

    def indicate_ordered(self) :
        self.rp_dict['ordered'] = 1
        self.rp_dict['seq'] = self.seq
        self.trans_dict.emit(self.rp_dict)      ## INDICATE : ordered

    def indicate_release(self) :
        self.rp_dict['ordered'] = 2
        self.rp_dict['seq'] = self.seq
        self.trans_dict.emit(self.rp_dict)      ## INDICATE : ordered
    def receive_tr_data(self, screen_no, rqname, trcode, recordname, prev_next, data_len, err_code, msg1, msg2):
        if rqname == "check_deposit":
            self.check_deposit_2(rqname, trcode, recordname)

        elif "check_jumun" in rqname :
            item_code = rqname[0:6]
            self.res_check_jumun(rqname, trcode, recordname, item_code)
    
    def func_INSERT_db_item(self, code, step, ordered, orderType, perlow):
        conn = sqlite3.connect("item_status.db")
        cur = conn.cursor()
        sql = "insert into STATUS (code, step, ordered, orderType, perlow) values(:CODE, :STEP, :ORDERED, :ORDERTYPE, :PERLOW)"
        cur.execute(sql, {"CODE" : code, "STEP" : step, "ORDERED" : ordered, "ORDERTYPE" : orderType, "PERLOW" : perlow})
        conn.commit()
        conn.close()
        print(self.now(), "[WORKER] [func_INSERT_db_item] : INSERTED")

    def func_DELETE_db_item(self, code):
        conn = sqlite3.connect("item_status.db")
        cur = conn.cursor()
        sql = "delete from STATUS where code = :CODE"
        cur.execute(sql, {"CODE" : code})
        conn.commit()
        conn.close()
        print(self.now(), "[ TH", self.seq, "] [func_DELETE_db_item] DELETED : ", code)

    def now(self) :
        return datetime.datetime.now()

    def get_now(self) :

        year = strftime("%Y", localtime())
        month = strftime("%m", localtime())
        day = strftime("%d", localtime())
        hour = strftime("%H", localtime())
        cmin = strftime("%M", localtime())
        sec = strftime("%S", localtime())

        now = "[" + year + "/" + month +"/" + day + " " + hour + ":" + cmin + ":" + sec + "] "

        return now

    # def func_INIT_db_item(self) :
    #     conn = sqlite3.connect("item_status.db")
    #     cur = conn.cursor()
    #     tablename = "item" + str(self.seq)
    #     sql = "create table if not exists " + tablename + " (code text, step integer)"
    #     cur.execute(sql)
    #     conn.commit()
    #     conn.close()

    #     print(tablename, "item db is initiated")

    #     self.func_DELETEALL_db_item()

    # def func_DELETEALL_db_item(self):
    #     conn = sqlite3.connect("item_status.db")
    #     cur = conn.cursor()
    #     tablename = "item" + str(self.seq)
    #     sql = "delete from " + tablename
    #     cur.execute(sql)
    #     conn.commit()
    #     conn.close()
    #     print(tablename, "items are deleted")