import sys
import time
import datetime
import pandas as pd
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
import module_delay

ACCOUNT = config.ACCOUNT
PASSWORD = config.PASSWORD

TAX = config.TAX
FEE_BUY = config.FEE_BUY
FEE_SELL = config.FEE_SELL
GOAL_PER = config.GOAL_PER
MAKE_ORDER = config.MAKE_ORDER
PER_LOW = config.PER_LOW
STEP_LIMIT = config.STEP_LIMIT

JUDGE_SHOW = 0

class Worker(QThread):
    connected = 0
    trans_dict = pyqtSignal(dict)
    th_con = pyqtSignal(int)
    rq_order = pyqtSignal(dict)

    def __init__(self, seq):
        super().__init__()
        self.seq = seq
        self.PER_HI = 0.5
        self.items = deque()
        
        self.prev_price = 0
        self.first_rcv = 1

        
        self.delay_item = ''

        self.ordering_item_code = 0
        self.ordering_qty = 0
        self.ordering_price = 0
        self.ordering_ordertype = 0

    def event_connect(self, err_code):
        if err_code == 0:
            self.connected = 1
        else:
            print(self.now(), "[ TH", self.seq, "] [event_connect] thread disconnected")

    def run(self):
        self.lock = 0       ## lock variable initialize
        self.cnt = 0
        print(self.now(), "[ TH", self.seq, "] [run] Thread Connected")
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
                    # print(now, "[ TH", self.seq, "]", "[che_result] orderType : ", orderType)
                    cur_step = self.func_GET_db_item(item_code, 1)          ## DB : step -> cur_step
                    new_step = cur_step + 1
                    if self.func_UPDATE_db_item(item_code, 1, new_step) == 1 :   ## update step
                        if self.func_UPDATE_db_item(item_code, 2, 0) == 1:       ## ordered -> 0
                            if self.func_UPDATE_db_item(item_code, 3, 0) == 1:       ## orderType -> 0
                                self.lock = 0           ## unlock

                ## Sell & Buy(SELL)
                elif orderType == 2 :
                    # print(now, "[ TH", self.seq, "]", "[che_result] orderType : ", orderType)
                    if self.func_UPDATE_db_item(item_code, 3, 4) == 1:       ## orderType -> 4
                        self.lock = 0           ## unlock

                ## full sell
                elif orderType == 3 :
                    # print(now, "[ TH", self.seq, "]", "[che_result] orderType : ", orderType)
                    self.func_DELETE_db_item(item_code)     ## DB : DELETE Item
                    self.lock = 0           ## unlock

                ## Sell & Buy(BUY)
                elif orderType == 4 :
                    # print(now, "[ TH", self.seq, "]", "[che_result] orderType : ", orderType)
                    if self.func_UPDATE_db_item(item_code, 2, 0) == 1:       ## ordered -> 0
                        if self.func_UPDATE_db_item(item_code, 3, 0) == 1:       ## orderType -> 0
                            self.lock = 0           ## unlock

                ## new BUY(Manual)
                elif orderType == 5 :
                    # print(now, "[ TH", self.seq, "]", "[che_result] orderType : ", orderType)
                    if self.func_UPDATE_db_item(item_code, 2, 0) == 1:       ## ordered -> 0
                        if self.func_UPDATE_db_item(item_code, 3, 0) == 1:       ## orderType -> 0
                            self.lock = 0           ## unlock

                ## gi BUY(Manual)
                elif orderType == 6 :
                    # print(now, "[ TH", self.seq, "]", "[che_result] orderType : ", orderType)
                    if self.func_UPDATE_db_item(item_code, 2, 0) == 1:       ## ordered -> 0
                        if self.func_UPDATE_db_item(item_code, 3, 0) == 1:       ## orderType -> 0
                            self.lock = 0           ## unlock

                ## partial SELL(Manual)
                elif orderType == 7 :
                    # print(now, "[ TH", self.seq, "]", "[che_result] orderType : ", orderType)
                    if self.func_UPDATE_db_item(item_code, 2, 0) == 1:       ## ordered -> 0
                        if self.func_UPDATE_db_item(item_code, 3, 0) == 1:       ## orderType -> 0
                            self.lock = 0           ## unlock

                ## FULL SELL(Manual)
                elif orderType == 8 :
                    # print(now, "[ TH", self.seq, "]", "[che_result] orderType : ", orderType)
                    self.func_DELETE_db_item(item_code)     ## DB : DELETE Item
                    self.lock = 0           ## unlock

                ## new BUY(item finder)
                elif orderType == 9 :
                    # print(now, "[ TH", self.seq, "]", "[che_result] orderType : ", orderType)
                    if self.func_UPDATE_db_item(item_code, 2, 0) == 1:       ## ordered -> 0
                        if self.func_UPDATE_db_item(item_code, 3, 0) == 1:       ## orderType -> 0
                            self.lock = 0           ## unlock

    @pyqtSlot(int)
    def resume_thread(self, data) :
        self.delay.terminate()

        if data == self.seq : 
            item_code = self.delay_item
            orderType = self.func_GET_db_item(item_code, 3)

            if orderType != "none" :                ## after get data from db
                if orderType == 1 :                                             ## add water
                    if self.func_UPDATE_db_item(item_code, 2, 0) == 1:       ## ordered -> 0
                        self.indicate_release()
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

    def pause_worker(self, item_code) :
        self.rp_dict = {}
        self.delay = module_delay.Delay(self.seq)
        self.delay.resume.connect(self.resume_thread)
        self.delay_item = item_code
        self.indicate_paused()
        self.delay.start()

    # def func_test(self, item_code, qty, price, ordertype) :
    #     print("func test")
    #     self.ordering_item_code = item_code
    #     self.ordering_qty = qty
    #     self.ordering_price = price
    #     self.ordering_ordertype = ordertype

    #     self.kiwoom.dynamicCall("SetInputValue(QString, QString)", "계좌번호", ACCOUNT)
    #     self.kiwoom.dynamicCall("SetInputValue(QString, QString)", "비밀번호", PASSWORD)
    #     self.kiwoom.dynamicCall("CommRqData(QString, QString, int, QString)", "check_deposit", "opw00001", 0, "0101")

    # def check_deposit_2(self, rqname, trcode, recordname) :
    #     print("check_deposit_2")
    #     deposit = self.kiwoom.dynamicCall("GetCommData(QString, QString, int, QString)", trcode, recordname, 0, "예수금")
    #     d1 = self.kiwoom.dynamicCall("GetCommData(QString, QString, int, QString)", trcode, recordname, 0, "d+1추정예수금")
    #     d2 = self.kiwoom.dynamicCall("GetCommData(QString, QString, int, QString)", trcode, recordname, 0, "d+2추정예수금")

    #     purchase_price = self.ordering_price * self.ordering_qty

    #     print("pu price : ", purchase_price)

    #     if d2 >= purchase_price :
    #         print("d2 over")
    #         if self.ordering_ordertype == 5 :
    #             print("ordertype 5")
    #             self.func_INSERT_db_item(item_code, 0, 0, 0, 0)             ## 신규 item db insert
    #             if self.func_UPDATE_db_item(item_code, 2, 1) == 1:          ## ordered -> 1
    #                 if self.func_UPDATE_db_item(item_code, 3, 5) == 1:       ## orderType -> 5(manual buy)
    #                     order = {}
    #                     order['type'] = 0       ## buy
    #                     order['item_code'] = item_code
    #                     order['qty'] = qty
    #                     order['price'] = price
    #                     order['order_type'] = orderType
    #                     self.rq_order.emit(order)

    @pyqtSlot(dict)
    def dict_from_main(self, data) :
        item_code = data['item_code']
        deposit = data['deposit']

        if data['autoTrade'] == 0 :                                             ## manual trading 시
            self.lock = 1
            orderType = data['orderType']
            if orderType == 5 :                                                 ## 신규 item manual 매수
                if MAKE_ORDER == 1 :
                    qty = data['qty']
                    price = data['price']

                    # self.func_test(item_code, qty, price, orderType)

                    self.func_INSERT_db_item(item_code, 0, 0, 0, 0)             ## 신규 item db insert

                    if self.func_UPDATE_db_item(item_code, 2, 1) == 1:          ## ordered -> 1
                        if self.func_UPDATE_db_item(item_code, 3, 5) == 1:       ## orderType -> 5(manual buy)
                            order = {}
                            order['type'] = 0       ## buy
                            order['item_code'] = item_code
                            order['qty'] = qty
                            order['price'] = price
                            order['order_type'] = orderType
                            self.rq_order.emit(order)


            elif orderType == 9 :         ## 신규 item item finding 매수
                if MAKE_ORDER == 1 :
                    qty = data['qty']
                    price = data['price']

                    self.func_INSERT_db_item(item_code, 0, 0, 0, 0)     ## 신규 item db insert

                    if self.func_UPDATE_db_item(item_code, 2, 1) == 1:       ## ordered -> 1
                        if self.func_UPDATE_db_item(item_code, 3, 9) == 1:       ## orderType -> 9(manual item finding buy)
                            order = {}
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
                            order['type'] = 1      ## sell
                            order['item_code'] = item_code
                            order['qty'] = qty
                            order['price'] = price
                            order['order_type'] = orderType
                            self.indicate_ordered()         ## INDICATE : ordered
                            self.rq_order.emit(order)

                            # print(self.now(), "[ TH", self.seq, "] [dict_from_main] Full Sell Manual : ", item_code)

        elif data['autoTrade'] == 1 :                   ## auto trading 시
            if self.first_rcv == 1 :
                # print(now, "[ TH", self.seq, "]", "First Receive")
                self.prev_price = data['cur_price']
                self.TA_UNIT_SUM = 0
                self.val_cnt = 0

                # ordered = self.func_GET_db_item(item_code, 2)
                # if ordered == 1 :       ## 프로그램이 시작했는데 현재 item이 order 중인 경우
                if self.func_GET_db_item(item_code, 2) == 1 :           ## 프로그램이 시작했는데 현재 item이 order 중인 경우 
                    self.lock = 1

                    ## SHOW ##
                    own_count = data['own_count']
                    unit_price = data['unit_price']
                    cur_price = data['cur_price']
                    price_buy = data['price_buy']
                    price_sell = data['price_sell']
                    chegang = data['chegang']

                    total_purchase = own_count * unit_price
                    total_evaluation = own_count * price_buy    ## 매수 최우선가 기준으로 계산
                    temp_total = total_evaluation - total_purchase
                    fee_buy = FEE_BUY * total_purchase
                    fee_sell = FEE_SELL * total_evaluation
                    tax = TAX * total_evaluation
                    total_fee = round((fee_buy + fee_sell + tax), 1)
                    total_sum = total_evaluation - total_purchase - total_fee
                    percent = round((total_sum / total_purchase) * 100, 1)
                    step = self.func_GET_db_item(item_code, 1)

                    self.rp_dict = {}
                    self.rp_dict.update(data)

                    self.rp_dict['ordered'] = 0
                    self.rp_dict['total_purchase'] = total_purchase
                    self.rp_dict['total_evaluation'] = total_evaluation
                    self.rp_dict['temp_total'] = temp_total
                    self.rp_dict['total_fee'] = total_fee
                    self.rp_dict['total_sum'] = total_sum
                    self.rp_dict['percent'] = percent
                    self.rp_dict['step'] = step
                    self.rp_dict['seq'] = self.seq
                    self.rp_dict['high'] = self.PER_HI

                    self.indicate_ordered()         ## INDICATE : ordered
                    self.trans_dict.emit(self.rp_dict)       ## SHOW
                
                self.first_rcv = 0
            else :      ## 2번째 receive 부터
                if self.lock == 0 :
                    self.lock = 1       ## lock 체결
                    
                    step = self.func_GET_db_item(item_code, 1)

                    ## SHOW -> TABLE ##
                    own_count = data['own_count']
                    unit_price = data['unit_price']
                    cur_price = data['cur_price']
                    price_buy = data['price_buy']
                    price_sell = data['price_sell']
                    chegang = data['chegang']

                    total_purchase = own_count * unit_price
                    total_evaluation = own_count * price_buy    ## 매수 최우선가 기준
                    temp_total = total_evaluation - total_purchase
                    fee_buy = FEE_BUY * total_purchase
                    fee_sell = FEE_SELL * total_evaluation
                    tax = TAX * total_evaluation
                    total_fee = round((fee_buy + fee_sell + tax), 1)
                    total_sum = total_evaluation - total_purchase - total_fee
                    percent = round((total_sum / total_purchase) * 100, 1)
                    step = self.func_GET_db_item(item_code, 1)

                    self.rp_dict = {}
                    self.rp_dict.update(data)
                    self.rp_dict['ordered'] = 0
                    self.rp_dict['total_purchase'] = int(total_purchase)
                    self.rp_dict['total_evaluation'] = int(total_evaluation)
                    self.rp_dict['temp_total'] = int(temp_total)
                    self.rp_dict['total_fee'] = int(total_fee)
                    self.rp_dict['total_sum'] = int(total_sum)
                    self.rp_dict['percent'] = percent
                    self.rp_dict['step'] = step
                    self.rp_dict['seq'] = self.seq
                    self.rp_dict['high'] = self.PER_HI

                    self.trans_dict.emit(self.rp_dict)       

                    ## Make Order
                    # orderType = self.func_GET_db_item(item_code, 3)

                    # if orderType == 4 :
                    #     print(now, "[ TH", self.seq, "]", "sell and buy - sell : terminated")
                        # if MAKE_ORDER == 1 :
                        #     qty = self.func_GET_db_item(item_code, 4)       ## DB : qty <- trAmount
                        #     price = price_buy

                        #     print(now, "[ TH", self.seq, "]", "make order : ", item_code, "SELL & BUY(BUY")
                        #     order = {}
                        #     order['type'] = 0       ## buy
                        #     order['item_code'] = item_code
                        #     order['qty'] = qty
                        #     order['price'] = price
                        #     self.rq_order.emit(order)
                        #     self.indicate_ordered()         ## INDICATE : ordered

                    # else :
                    res = self.judge(percent, step, own_count, price_buy, price_sell, total_purchase, total_evaluation, chegang)
                    judge_type = res['judge']

                    if judge_type == 0 :        ## stay
                        self.lock = 0
                        # print(now, "[ TH", self.seq, "]", item_code, "judge : 0")

                    elif judge_type == 1 :      ## add water
                        # print(now, "[ TH", self.seq, "]", item_code, "judge : 1")
                        if MAKE_ORDER == 1 :
                            qty = res['qty']
                            price = res['price']
                            if qty < 0 :
                                # print(now, "[ TH", self.seq, "]", "qty is under 0")
                                self.lock = 0

                            elif qty >= 0 :
                                if self.func_UPDATE_db_item(item_code, 2, 1) == 1:       ## ordered -> 1
                                    if self.func_UPDATE_db_item(item_code, 3, 1) == 1:       ## orderType -> 1
                                        order = {}
                                        order['type'] = 0       ## buy
                                        order['item_code'] = item_code
                                        order['qty'] = qty
                                        order['price'] = price
                                        order['order_type'] = judge_type
                                        self.indicate_ordered()         ## INDICATE : ordered
                                        self.rq_order.emit(order)       ## make order to master

                                        # print(self.now(), "[ TH", self.seq, "] [dict_from_main] Add Water : ", item_code)
                                        

                    # elif judge_type == 2 :      ## sell & buy
                    #     # if JUDGE_SHOW == 1 :
                    #     #     print(now, "[ TH", self.seq, "]", item_code, "judge : 2")
                    #     if MAKE_ORDER == 1 :
                    #         qty = res['sell_qty']
                    #         price = res['sell_price']

                    #         if qty == 0 :
                    #             print(now, "[ TH", self.seq, "]", item_code, "judge : 2 and 3")
                    #             qty = own_count
                    #             if self.func_UPDATE_db_item(item_code, 2, 1) == 1:      ## ordered 변경 -> 1
                    #                 if self.func_UPDATE_db_item(item_code, 3, 3) == 1:  ## orderType 변경 -> 3
                    #                     order = {}
                    #                     order['type'] = 1       ## sell
                    #                     order['item_code'] = item_code
                    #                     order['qty'] = qty
                    #                     order['price'] = price
                    #                     order['order_type'] = judge_type
                    #                     self.indicate_ordered()         ## INDICATE : ordered
                    #                     self.rq_order.emit(order)

                    #                     # print(self.now(), "[ TH", self.seq, "] [dict_from_main] Sell & Buy(sell) : ", item_code)

                    #         elif qty >= 1 :
                    #             if self.func_UPDATE_db_item(item_code, 2, 1) == 1:       ## ordered -> 1
                    #                 if self.func_UPDATE_db_item(item_code, 3, 2) == 1:      ## orderType -> 2
                    #                     if self.func_UPDATE_db_item(item_code, 4, qty) == 1:    ## 판매수량 -> trAmount
                    #                         order = {}
                    #                         order['type'] = 1       ## sell
                    #                         order['item_code'] = item_code
                    #                         order['qty'] = qty
                    #                         order['price'] = price
                    #                         self.indicate_ordered()         ## INDICATE : ordered
                    #                         self.rq_order.emit(order)

                    #                         # print(self.now(), "[ TH", self.seq, "] [dict_from_main] Sell & Buy(sell) : ", item_code)

                    elif judge_type == 3 :      ## full_sell
                        if MAKE_ORDER == 1 :
                            # qty = res['qty']
                            if self.func_UPDATE_db_item(item_code, 2, 1) == 1:      ## ordered 변경 -> 1
                                if self.func_UPDATE_db_item(item_code, 3, 3) == 1:  ## orderType 변경 -> 3
                                    order = {}
                                    order['type'] = 1       ## sell
                                    order['item_code'] = item_code
                                    order['qty'] = res['qty']       ## 전량
                                    order['price'] = res['price']   ## 매수 최우선가
                                    order['order_type'] = judge_type
                                    self.indicate_ordered()         ## INDICATE : ordered
                                    self.rq_order.emit(order)       ## make order to master

                                    # print(self.now(), "[ TH", self.seq, "] [dict_from_main] Full Sell Auto : ", item_code)

        ################## judgement ###################
    def judge(self, percent, step, own_count, price_buy, price_sell, total_purchase, total_evaluation, chegang) :
        res = {}
        # Add Water
        if percent < PER_LOW and step < STEP_LIMIT :
            PS = int(price_sell)                # 매도 최우선가
            PB = int(price_buy)                 # 매수 최우선가
            A = total_purchase              # 총 매입금액
            B = total_evaluation            # 총 평가금액
            T = TAX
            FB = FEE_BUY
            FS = FEE_SELL
            P = GOAL_PER

            X = 1 + P + FB
            Y = 1 - T - FS
            buy_qty = math.ceil((Y*B - X*A) / (PS*X - PB*Y))

            res['judge'] = 1
            res['qty'] = buy_qty
            res['price'] = int(price_sell)      ## 매도 최우선가

            return res

        # Sell & Buy
        # elif percent > self.PER_HI and step < STEP_LIMIT :
        #     # sell_qty = int(own_count / 2)
        #     sell_qty = own_count
        #     # if sell_qty == 0 :
        #     #     sell_qty = 1
        #     price = int(price_sell)

        #     # res['judge'] = 2
        #     res['judge'] = 3
        #     res['qty'] = own_count
        #     res['price'] = int(price_buy)

        #     return res
        
        # Full Sell
        elif percent > self.PER_HI and step <= STEP_LIMIT :
            sell_qty = own_count

            res['judge'] = 3
            res['qty'] = own_count  ## 전량
            res['price'] = int(price_buy)   ## 매수최우선가

            return res

        # # # 손절 1단계
        # elif percent < PER_LOW and step == STEP_LIIT :
        #     # if chegang >= 90 :
        #     sell_qty = own_count
        #     price = int(price_sell)

        #     res['judge'] = 3
        #     res['sell_qty'] = sell_qty
        #     res['sell_price'] = price

        #     return res

        # STAY
        else :
            res['judge'] = 0

            return res
            
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
            elif col == 4:      # get trAmount
                sql = "select trAmount from STATUS where code = ?"
                cur.execute(sql, [code])

            row = cur.fetchone()
            conn.close()

            if row is None:
                return "none"
            else:
                return row[0]
    def func_INSERT_db_item(self, code, step, ordered, orderType, trAmount):
        conn = sqlite3.connect("item_status.db")
        cur = conn.cursor()
        sql = "insert into STATUS (code, step, ordered, orderType, trAmount) values(:CODE, :STEP, :ORDERED, :ORDERTYPE, :TRAMOUNT)"
        cur.execute(sql, {"CODE" : code, "STEP" : step, "ORDERED" : ordered, "ORDERTYPE" : orderType, "TRAMOUNT" : trAmount})
        conn.commit()
        conn.close()
        print(self.now(), "[ TH", self.seq, "] [func_INSERT_db_item] INSERTED : ", code, step, ordered, orderType, trAmount)
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
        elif col == 4:  # update trAmount
            sql = "update STATUS set trAmount = :DATA where code = :CODE"    
            cur.execute(sql, {"DATA" : data, "CODE" : code})

        conn.commit()
        conn.close()
        success = cur.rowcount
        # print(now, "[ TH", self.seq, "]", "UPDATED")
        return success
    def func_DELETE_db_item(self, code):
        conn = sqlite3.connect("item_status.db")
        cur = conn.cursor()
        sql = "delete from STATUS where code = :CODE"
        cur.execute(sql, {"CODE" : code})
        conn.commit()
        conn.close()
        print(self.now(), "[ TH", self.seq, "] [func_DELETE_db_item] DELETED : ", code)

    def indicate_ordered(self) :
        self.rp_dict['ordered'] = 1
        self.rp_dict['seq'] = self.seq
        self.trans_dict.emit(self.rp_dict)      ## INDICATE : ordered

    def indicate_paused(self) :
        self.rp_dict['ordered'] = 3
        self.rp_dict['seq'] = self.seq
        self.trans_dict.emit(self.rp_dict)      ## INDICATE : ordered

    def indicate_release(self) :
        self.rp_dict['ordered'] = 2
        self.rp_dict['seq'] = self.seq
        self.trans_dict.emit(self.rp_dict)      ## INDICATE : ordered
    # def check_deposit_1(self) :
    #     self.kiwoom.dynamicCall("SetInputValue(QString, QString)", "계좌번호", ACCOUNT)
    #     self.kiwoom.dynamicCall("SetInputValue(QString, QString)", "비밀번호", PASSWORD)
    #     self.kiwoom.dynamicCall("CommRqData(QString, QString, int, QString)", "check_deposit", "opw00001", 0, "0101")
    # def check_deposit_2(self, rqname, trcode, recordname) :
    #     deposit = self.kiwoom.dynamicCall("GetCommData(QString, QString, int, QString)", trcode, recordname, 0, "예수금")
    #     d_1 = self.kiwoom.dynamicCall("GetCommData(QString, QString, int, QString)", trcode, recordname, 0, "d+1추정예수금")
    #     d_2 = self.kiwoom.dynamicCall("GetCommData(QString, QString, int, QString)", trcode, recordname, 0, "d+2추정예수금")
    #     # orderable_money = self.kiwoom.dynamicCall("GetCommData(QString, QString, int, QString)", trcode, recordname, 0, "주문가능금액")

    #     # str('{0:,}'.format())
    #     self.wid_show_deposit.setText(str('{0:,}'.format(int(deposit))))
    #     self.wid_show_deposit_d1.setText(str('{0:,}'.format(int(d_1))))
    #     self.wid_show_deposit_d2.setText(str(int(d_2)))
    #     # self.wid_show_orderable_money.setText(str('{0:,}'.format(int(orderable_money))))

    #     self.set_deposit = 1
    def receive_tr_data(self, screen_no, rqname, trcode, recordname, prev_next, data_len, err_code, msg1, msg2):
        if rqname == "check_deposit":
            self.check_deposit_2(rqname, trcode, recordname)
    def now(self) :
        return datetime.datetime.now()