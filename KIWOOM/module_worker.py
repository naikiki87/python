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

TAX = 0.0025
FEE_BUY = 0.0035
FEE_SELL = 0.0035
GOAL_PER = -0.015
MAKE_ORDER = 1
PER_LOW = -2

STEP_LIMIT = 5
TA_UNIT = 10
JUDGE_SHOW = 0
# ACCOUNT = "8137639811"
ACCOUNT = "8144126111"
PASSWORD = "6458"

class Worker(QThread):
    connected = 0
    trans_dict = pyqtSignal(dict)
    th_con = pyqtSignal(int)
    notice = pyqtSignal(dict)
    rq_order = pyqtSignal(dict)

    def __init__(self, seq):
        now = self.now()
        super().__init__()
        self.seq = seq

        self.jump_step = 0

        self.PER_HI = 0.5
        self.items = deque()
        
        self.prev_price = 0
        self.value10 = []
        self.trend_cnt = 0
        self.df_trend = pd.DataFrame(columns = ['avg'])
        self.first_rcv = 1

    def event_connect(self, err_code):
        now = self.now()
        if err_code == 0:
            self.connected = 1
        else:
            print(now, "[ TH", self.seq, "]", "thread disconnected")

    def run(self):
        now = self.now()
        self.lock = 0       ## lock variable initialize
        self.cnt = 0
        print(now, "[ TH", self.seq, "]", "connected")
        self.th_con.emit(1)

        # while True:
        #     try:
        #         print(now, "[ TH", self.seq, "]", "con : ", self.connected)
        #         if self.connected == 1:
        #             self.th_con.emit(1)
        #             break
        #         time.sleep(1)
        #     except:
        #         pass
    
    @pyqtSlot(dict)
    def che_result(self, data) :
        now = self.now()
        if data['th_num'] == self.seq :
            print(now, "[ TH", self.seq, "]", " CHEJAN DATA RECEIVED")

            item_code = data['item_code']
            orderType = self.func_GET_db_item(item_code, 3)
            res = data['res']

            if res == 1 :   ## 정상처리 되었을 경우
                ## Add water
                if orderType == 1 :
                    print(now, "[ TH", self.seq, "]", "[che_result] orderType : ", orderType)
                    cur_step = self.func_GET_db_item(item_code, 1)          ## DB : step -> cur_step
                    new_step = cur_step + 1
                    if self.func_UPDATE_db_item(item_code, 1, new_step) == 1 :   ## update step
                        if self.func_UPDATE_db_item(item_code, 2, 0) == 1:       ## ordered -> 0
                            if self.func_UPDATE_db_item(item_code, 3, 0) == 1:       ## orderType -> 0
                                self.lock = 0           ## unlock

                ## Sell & Buy(SELL)
                elif orderType == 2 :
                    print(now, "[ TH", self.seq, "]", "[che_result] orderType : ", orderType)
                    if self.func_UPDATE_db_item(item_code, 3, 4) == 1:       ## orderType -> 4
                        self.lock = 0           ## unlock

                ## full sell
                elif orderType == 3 :
                    print(now, "[ TH", self.seq, "]", "[che_result] orderType : ", orderType)
                    self.func_DELETE_db_item(item_code)     ## DB : DELETE Item
                    self.lock = 0           ## unlock

                ## Sell & Buy(BUY)
                elif orderType == 4 :
                    print(now, "[ TH", self.seq, "]", "[che_result] orderType : ", orderType)
                    if self.func_UPDATE_db_item(item_code, 2, 0) == 1:       ## ordered -> 0
                        if self.func_UPDATE_db_item(item_code, 3, 0) == 1:       ## orderType -> 0
                            self.lock = 0           ## unlock

                ## new BUY(Manual)
                elif orderType == 5 :
                    print(now, "[ TH", self.seq, "]", "[che_result] orderType : ", orderType)
                    if self.func_UPDATE_db_item(item_code, 2, 0) == 1:       ## ordered -> 0
                        if self.func_UPDATE_db_item(item_code, 3, 0) == 1:       ## orderType -> 0
                            self.lock = 0           ## unlock

                ## gi BUY(Manual)
                elif orderType == 6 :
                    print(now, "[ TH", self.seq, "]", "[che_result] orderType : ", orderType)
                    if self.func_UPDATE_db_item(item_code, 2, 0) == 1:       ## ordered -> 0
                        if self.func_UPDATE_db_item(item_code, 3, 0) == 1:       ## orderType -> 0
                            self.lock = 0           ## unlock

                ## partial SELL(Manual)
                elif orderType == 7 :
                    print(now, "[ TH", self.seq, "]", "[che_result] orderType : ", orderType)
                    if self.func_UPDATE_db_item(item_code, 2, 0) == 1:       ## ordered -> 0
                        if self.func_UPDATE_db_item(item_code, 3, 0) == 1:       ## orderType -> 0
                            self.lock = 0           ## unlock

                ## FULL SELL(Manual)
                elif orderType == 8 :
                    print(now, "[ TH", self.seq, "]", "[che_result] orderType : ", orderType)
                    self.func_DELETE_db_item(item_code)     ## DB : DELETE Item
                    self.lock = 0           ## unlock
            
            elif res == 0 : ## 수량부족 또는 order 미수신으로 처리 불가시
                if orderType == 5 :         # 신규 buy인 경우 db삭제 및 lock 해제
                    print(now, "[ TH", self.seq, "]", "[che_result] orderType : ", orderType)
                    self.func_DELETE_db_item(item_code)     ## DB : DELETE Item
                    self.lock = 0           ## unlock

                else :                      # 다른 sit인 경우 db order 정보 0으로 세팅 및 lock 해제
                    print(now, "[ TH", self.seq, "]", "[che_result] orderType : ", orderType)
                    if self.func_UPDATE_db_item(item_code, 2, 0) == 1:       ## ordered -> 0
                        self.lock = 0           ## unlock


    @pyqtSlot(dict)
    def dict_from_main(self, data) :
        now = self.now()
        item_code = data['item_code']
        deposit = data['deposit']

        if data['autoTrade'] == 0 :             ## manual trading 시
            self.lock = 1
            print(now, "[ TH", self.seq, "]", "Receive Manual dict")
            orderType = data['orderType']
            if orderType == 5 :         ## 신규 item 매수
                if MAKE_ORDER == 1 :
                    print(now, "[ TH", self.seq, "]", "신규 바이")
                    qty = data['qty']
                    price = data['price']

                    self.func_INSERT_db_item(item_code, 0, 0, 0, 0)     ## 신규 item db insert

                    if self.func_UPDATE_db_item(item_code, 2, 1) == 1:       ## ordered -> 1
                        if self.func_UPDATE_db_item(item_code, 3, 5) == 1:       ## orderType -> 5(manual buy)
                            print(now, "[ TH", self.seq, "]", " thread setting complete -> ordertype : 5")
                            print(now, "[ TH", self.seq, "]", "make order : ", item_code, "BUY(MANUAL)")

                            order = {}
                            order['type'] = 0       ## buy
                            order['item_code'] = item_code
                            order['qty'] = qty
                            order['price'] = price
                            order['order_type'] = orderType
                            self.rq_order.emit(order)
            elif orderType == 6 :       ## 기존 item 수동 매수
                if MAKE_ORDER == 1 :
                    print(now, "[ TH", self.seq, "]", "th 기 바이")
                    qty = data['qty']
                    price = data['price']

                    if self.func_UPDATE_db_item(item_code, 2, 1) == 1:       ## ordered -> 1
                        if self.func_UPDATE_db_item(item_code, 3, 6) == 1:       ## orderType -> 6(manual gi buy)
                            print(now, "[ TH", self.seq, "]", " thread setting complete -> ordertype : 6")
                            print(now, "[ TH", self.seq, "]", "make order : ", item_code, "GI BUY(MANUAL)")

                            order = {}
                            order['type'] = 0       ## buy
                            order['item_code'] = item_code
                            order['qty'] = qty
                            order['price'] = price
                            order['order_type'] = orderType
                            self.rq_order.emit(order)
                            self.indicate_ordered()         ## INDICATE : ordered
            elif orderType == 7 :       ## 일부 sell manual
                if MAKE_ORDER == 1 :
                    qty = data['qty']
                    price = data['price']

                    if self.func_UPDATE_db_item(item_code, 2, 1) == 1:      ## ordered 변경 -> 1
                        if self.func_UPDATE_db_item(item_code, 3, 7) == 1:  ## orderType 변경 -> 7(manual sell)
                            print(now, "[ TH", self.seq, "]", "make order : ", item_code, "SELL(MANUAL)")

                            order = {}
                            order['type'] = 1       ## sell
                            order['item_code'] = item_code
                            order['qty'] = qty
                            order['price'] = price
                            order['order_type'] = orderType
                            self.rq_order.emit(order)
                            self.indicate_ordered()         ## INDICATE : ordered
            elif orderType == 8 :       ## full sell manual
                if MAKE_ORDER == 1 :
                    qty = data['qty']
                    price = data['price']

                    if self.func_UPDATE_db_item(item_code, 2, 1) == 1:      ## ordered 변경 -> 1
                        if self.func_UPDATE_db_item(item_code, 3, 8) == 1:  ## orderType 변경 -> 8(manual sell full)
                            print(now, "[ TH", self.seq, "]", "make order : ", item_code, "SELL FULL(MANUAL)")

                            order = {}
                            order['type'] = 1      ## sell
                            order['item_code'] = item_code
                            order['qty'] = qty
                            order['price'] = price
                            order['order_type'] = orderType
                            self.rq_order.emit(order)
                            self.indicate_ordered()         ## INDICATE : ordered

        elif data['autoTrade'] == 1 :                   ## auto trading 시
            if self.first_rcv == 1 :
                print(now, "[ TH", self.seq, "]", "First Receive")
                self.prev_price = data['cur_price']
                self.TA_UNIT_SUM = 0
                self.val_cnt = 0

                ordered = self.func_GET_db_item(item_code, 2)
                if ordered == 1 :       ## 프로그램이 시작했는데 현재 item이 order 중인 경우
                    self.lock = 1

                    ## SHOW ##
                    own_count = data['own_count']
                    unit_price = data['unit_price']
                    cur_price = data['cur_price']
                    price_buy = data['price_buy']
                    price_sell = data['price_sell']
                    chegang = data['chegang']

                    total_purchase = own_count * unit_price
                    # total_evaluation = own_count * cur_price
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

                    self.trans_dict.emit(self.rp_dict)       ## SHOW
                    self.indicate_ordered()         ## INDICATE : ordered
                
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
                    # total_evaluation = own_count * cur_price
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
                    orderType = self.func_GET_db_item(item_code, 3)

                    if orderType == 4 :
                        print(now, "[ TH", self.seq, "]", "sell and buy - sell : terminated")
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

                    else :
                        res = self.judge(percent, step, own_count, price_buy, price_sell, total_purchase, total_evaluation, chegang)
                        judge_type = res['judge']

                        if judge_type == 0 :        ## stay
                            if JUDGE_SHOW == 1 :
                                print(now, "[ TH", self.seq, "]", item_code, "judge : 0")
                            self.lock = 0

                        elif judge_type == 1 :      ## add water
                            if JUDGE_SHOW == 1 :
                                print(now, "[ TH", self.seq, "]", item_code, "judge : 1")
                            if MAKE_ORDER == 1 :
                                qty = res['qty']
                                price = res['price']
                                if qty < 0 :
                                    print(now, "[ TH", self.seq, "]", "qty is under 0")
                                    self.lock = 0

                                elif qty >= 0 :
                                    if self.func_UPDATE_db_item(item_code, 2, 1) == 1:       ## ordered -> 1
                                        if self.func_UPDATE_db_item(item_code, 3, 1) == 1:       ## orderType -> 1
                                            print(now, "[ TH", self.seq, "]", "make order : ", item_code, "BUY")

                                            order = {}
                                            order['type'] = 0       ## buy
                                            order['item_code'] = item_code
                                            # order['qty'] = res['qty']       ## judge를 통해 나온 수량
                                            order['qty'] = qty
                                            # order['price'] = res['price']   ## 매도 최우선가로 구매
                                            order['price'] = price
                                            order['order_type'] = judge_type
                                            self.rq_order.emit(order)       ## make order to master
                                            self.indicate_ordered()         ## INDICATE : ordered

                        elif judge_type == 2 :      ## sell & buy
                            if JUDGE_SHOW == 1 :
                                print(now, "[ TH", self.seq, "]", item_code, "judge : 2")
                            if MAKE_ORDER == 1 :

                                qty = res['sell_qty']
                                price = res['sell_price']

                                if qty == 0 :
                                    print(now, "[ TH", self.seq, "]", item_code, "judge : 2 and 3")
                                    qty = own_count
                                    if self.func_UPDATE_db_item(item_code, 2, 1) == 1:      ## ordered 변경 -> 1
                                        if self.func_UPDATE_db_item(item_code, 3, 3) == 1:  ## orderType 변경 -> 3
                                            print(now, "[ TH", self.seq, "]", "make order : ", item_code, "SELL & BUY(SELL")

                                            order = {}
                                            order['type'] = 1       ## sell
                                            order['item_code'] = item_code
                                            order['qty'] = qty
                                            order['price'] = price
                                            order['order_type'] = judge_type
                                            self.rq_order.emit(order)
                                            self.indicate_ordered()         ## INDICATE : ordered

                                elif qty >= 1 :
                                    if self.func_UPDATE_db_item(item_code, 2, 1) == 1:       ## ordered -> 1
                                        if self.func_UPDATE_db_item(item_code, 3, 2) == 1:      ## orderType -> 2
                                            if self.func_UPDATE_db_item(item_code, 4, qty) == 1:    ## 판매수량 -> trAmount
                                                print(now, "[ TH", self.seq, "]", "make order : ", item_code, "SELL")

                                                order = {}
                                                order['type'] = 1       ## sell
                                                order['item_code'] = item_code
                                                order['qty'] = qty
                                                order['price'] = price
                                                self.rq_order.emit(order)
                                                self.indicate_ordered()         ## INDICATE : ordered

                        elif judge_type == 3 :      ## full_sell
                            if JUDGE_SHOW == 1 :
                                print(now, "[ TH", self.seq, "]", item_code, "judge : 3")
                            if MAKE_ORDER == 1 :
                                qty = res['qty']
                                print(now, "[ TH", self.seq, "]", "qty : ", qty)
                                # qty = res['sell_qty']
                                # price = res['sell_price']

                                if self.func_UPDATE_db_item(item_code, 2, 1) == 1:      ## ordered 변경 -> 1
                                    if self.func_UPDATE_db_item(item_code, 3, 3) == 1:  ## orderType 변경 -> 3
                                        print(now, "[ TH", self.seq, "]", "make order : ", item_code, "SELL")

                                        order = {}
                                        order['type'] = 1       ## sell
                                        order['item_code'] = item_code
                                        order['qty'] = res['qty']       ## 전량
                                        order['price'] = res['price']   ## 매수 최우선가
                                        order['order_type'] = judge_type
                                        
                                        self.rq_order.emit(order)       ## make order to master
                                        self.indicate_ordered()         ## INDICATE : ordered
                        
    


        ################## judgement ###################
    def judge(self, percent, step, own_count, price_buy, price_sell, total_purchase, total_evaluation, chegang) :
        now = self.now()
        res = {}
        # Add Water
        if percent < PER_LOW and step < STEP_LIMIT :
            # V = int(price_buy)              # 매도 최우선가
            # V_1st_buy = int(price_sell)     # 매수 최우선가
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

            # buy_qty = math.ceil((B-A-B*T-A*FB-B*FS-A*P) / (V_1st_buy*P + V_1st_buy*T + FB + FS))
            buy_qty = math.ceil((Y*B - X*A) / (PS*X - PB*Y))

            res['judge'] = 1
            # res['buy_qty'] = buy_qty
            res['qty'] = buy_qty
            # res['buy_price'] = V
            res['price'] = int(price_sell)      ## 매도 최우선가

            print(now, "[ TH", self.seq, "]", "JUDGE : 1", buy_qty)

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
            # price = int(price_sell)

            res['judge'] = 3
            # res['sell_qty'] = sell_qty
            # res['sell_price'] = price
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
        now = self.now()
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
        now = self.now()
        conn = sqlite3.connect("item_status.db")
        cur = conn.cursor()
        sql = "insert into STATUS (code, step, ordered, orderType, trAmount) values(:CODE, :STEP, :ORDERED, :ORDERTYPE, :TRAMOUNT)"
        cur.execute(sql, {"CODE" : code, "STEP" : step, "ORDERED" : ordered, "ORDERTYPE" : orderType, "TRAMOUNT" : trAmount})
        conn.commit()
        conn.close()
        print(now, "[ TH", self.seq, "]", "data INSERTED")
    def func_UPDATE_db_item(self, code, col, data) :
        now = self.now()
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
        now = self.now()
        conn = sqlite3.connect("item_status.db")
        cur = conn.cursor()
        sql = "delete from STATUS where code = :CODE"
        cur.execute(sql, {"CODE" : code})
        conn.commit()
        conn.close()
        print(now, "[ TH", self.seq, "]", "data DELETED")

    def indicate_ordered(self) :
        now = self.now()
        self.rp_dict['ordered'] = 1
        self.rp_dict['seq'] = self.seq
        self.trans_dict.emit(self.rp_dict)      ## INDICATE : ordered
    
    def now(self) :
        return datetime.datetime.now()