import sys
import time
import pandas as pd
import sqlite3
import math
from time import localtime, strftime
from PyQt5.QtWidgets import *
from PyQt5.QAxContainer import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5 import QtTest, QtCore

TAX = 0.0025
FEE_BUY = 0.0035
FEE_SELL = 0.0035
GOAL_PER = -0.01
MAKE_ORDER = 1
PER_LOW = -2
PER_HI = 1
STEP_LIMIT = 5

ACCOUNT = "8137639811"
PASSWORD = "6458"

class Worker(QThread):
    connected = 0
    trans_dict = pyqtSignal(dict)
    th_con = pyqtSignal(int)
    notice = pyqtSignal(dict)

    def __init__(self, seq):
        super().__init__()
        self.seq = seq
        
        # self.MAKE_ORDER = 0
        # self.PER_LOW = -2
        # self.PER_HI = 2
        # self.STEP_LIMIT = 5
        self.first_rcv = 1
        self.worker = QAxWidget()
        self.worker.setControl("KHOPENAPI.KHOpenAPICtrl.1")
        self.worker.dynamicCall("CommConnect()")

        self.worker.OnEventConnect.connect(self.event_connect)

    def event_connect(self, err_code):
        if err_code == 0:
            self.connected = 1
        else:
            print("thread disconnected")

    def get_item_info(self):
        code = "005930"
        self.worker.dynamicCall("SetInputValue(QString, QString)", "종목코드", code)
        self.worker.dynamicCall("CommRqData(QString, QString, int, QString)", "opt10001_req", "opt10001", 0, "0101")

    def run(self):
        self.lock = 0       ## lock variable initialize
        self.cnt = 0
        while True:
            try:
                print("con : ", self.connected)
                if self.connected == 1:
                    self.th_con.emit(1)
                    break
                time.sleep(1)
            except:
                pass
    @pyqtSlot(dict)
    def start_work(self, data) :
        try :
            if data['start'] == 1 :
                self.MAKE_ORDER = data['start']
                self.PER_LOW = data['per_low']
                self.PER_HI = data['per_hi']
                self.STEP_LIMIT = data['step_limit']
                print("start work")
                print(self.PER_LOW)
                print(self.PER_HI)
                print(self.STEP_LIMIT)

            elif data['start'] == 0 :
                self.MAKE_ORDER = data['start']
                print("stop work")
        except :
            pass

    @pyqtSlot(dict)
    def che_result(self, data) :
        if data['th_num'] == self.seq :
            print(self.seq, " CHEJAN DATA RECEIVED")

            item_code = data['item_code']
            orderType = self.func_GET_db_item(item_code, 3)
            
            ## Add water
            if orderType == 1 :
                print("[th che_result] orderType : ", orderType)
                cur_step = self.func_GET_db_item(item_code, 1)          ## DB : step -> cur_step
                new_step = cur_step + 1
                if self.func_UPDATE_db_item(item_code, 1, new_step) == 1 :   ## update step
                    if self.func_UPDATE_db_item(item_code, 2, 0) == 1:       ## ordered -> 0
                        if self.func_UPDATE_db_item(item_code, 3, 0) == 1:       ## orderType -> 0
                            self.lock = 0           ## unlock

            ## Sell & Buy(SELL)
            elif orderType == 2 :
                print("[th che_result] orderType : ", orderType)
                if self.func_UPDATE_db_item(item_code, 3, 4) == 1:       ## orderType -> 4
                    self.lock = 0           ## unlock

            ## full sell
            elif orderType == 3 :
                print("[th che_result] orderType : ", orderType)
                self.func_DELETE_db_item(item_code)     ## DB : DELETE Item
                self.lock = 0           ## unlock

            ## Sell & Buy(BUY)
            elif orderType == 4 :
                print("[th che_result] orderType : ", orderType)
                if self.func_UPDATE_db_item(item_code, 2, 0) == 1:       ## ordered -> 0
                    if self.func_UPDATE_db_item(item_code, 3, 0) == 1:       ## orderType -> 0
                        self.lock = 0           ## unlock

            ## BUY(Manual)
            elif orderType == 5 :
                print("[th che_result] orderType : ", orderType)
                if self.func_UPDATE_db_item(item_code, 2, 0) == 1:       ## ordered -> 0
                    if self.func_UPDATE_db_item(item_code, 3, 0) == 1:       ## orderType -> 0
                        self.lock = 0           ## unlock

            ## BUY(Manual)
            elif orderType == 6 :
                print("[th che_result] orderType : ", orderType)
                if self.func_UPDATE_db_item(item_code, 2, 0) == 1:       ## ordered -> 0
                    if self.func_UPDATE_db_item(item_code, 3, 0) == 1:       ## orderType -> 0
                        self.lock = 0           ## unlock

            ## SELL(Manual)
            elif orderType == 7 :
                print("[th che_result] orderType : ", orderType)
                if self.func_UPDATE_db_item(item_code, 2, 0) == 1:       ## ordered -> 0
                    if self.func_UPDATE_db_item(item_code, 3, 0) == 1:       ## orderType -> 0
                        self.lock = 0           ## unlock

            ## FULL SELL(Manual)
            elif orderType == 8 :
                print("[th che_result] orderType : ", orderType)
                self.func_DELETE_db_item(item_code)     ## DB : DELETE Item
                self.lock = 0           ## unlock

    @pyqtSlot(dict)
    def dict_from_main(self, data) :
        item_code = data['item_code']
        # print("th dict : ", item_code)
        deposit = data['deposit']

        if self.first_rcv == 1 :
            ordered = self.func_GET_db_item(item_code, 2)
            if ordered == 1 :
                self.lock = 1

                ## SHOW ##
                own_count = data['own_count']
                unit_price = data['unit_price']
                cur_price = data['cur_price']
                price_buy = data['price_buy']
                price_sell = data['price_sell']

                total_purchase = own_count * unit_price
                total_evaluation = own_count * cur_price
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

                self.trans_dict.emit(self.rp_dict)       ## SHOW
                self.indicate_ordered()         ## INDICATE : ordered
            
            self.first_rcv = 0

        else :

            if data['autoTrade'] == 0 :
                self.lock = 1
                print("Receive Manual dict")

                orderType = data['orderType']

                if orderType == 5 :         ## 신규 item 매수
                    if MAKE_ORDER == 1 :
                        print("신규 바이")
                        qty = data['qty']
                        price = data['price']

                        self.func_INSERT_db_item(item_code, 0, 0, 0, 0)     ## 신규 item db insert

                        if self.func_UPDATE_db_item(item_code, 2, 1) == 1:       ## ordered -> 1
                            if self.func_UPDATE_db_item(item_code, 3, 5) == 1:       ## orderType -> 5(manual buy)
                                print(self.seq, " thread setting complete -> ordertype : 5")
                                print("make order : ", item_code, "BUY(MANUAL)")
                                self.ORDER_BUY(item_code, qty, price)    # ORDER : BUY

                elif orderType == 6 :       ## 기존 item 수동 매수
                    if MAKE_ORDER == 1 :
                        print("th 기 바이")
                        qty = data['qty']
                        price = data['price']

                        if self.func_UPDATE_db_item(item_code, 2, 1) == 1:       ## ordered -> 1
                            if self.func_UPDATE_db_item(item_code, 3, 6) == 1:       ## orderType -> 6(manual gi buy)
                                print(self.seq, " thread setting complete -> ordertype : 6")
                                print("make order : ", item_code, "GI BUY(MANUAL)")
                                
                                self.ORDER_BUY(item_code, qty, price)    # ORDER : BUY
                                self.indicate_ordered()         ## INDICATE : ordered

                elif orderType == 7 :       ## 일부 sell manual
                    if MAKE_ORDER == 1 :
                        qty = data['qty']
                        price = data['price']

                        if self.func_UPDATE_db_item(item_code, 2, 1) == 1:      ## ordered 변경 -> 1
                            if self.func_UPDATE_db_item(item_code, 3, 7) == 1:  ## orderType 변경 -> 7(manual sell)
                                print("make order : ", item_code, "SELL(MANUAL)")
                                
                                self.ORDER_SELL(item_code, qty, price)  # ORDER : SELL
                                self.indicate_ordered()         ## INDICATE : ordered

                elif orderType == 8 :       ## full sell manual
                    if MAKE_ORDER == 1 :
                        qty = data['qty']
                        price = data['price']

                        if self.func_UPDATE_db_item(item_code, 2, 1) == 1:      ## ordered 변경 -> 1
                            if self.func_UPDATE_db_item(item_code, 3, 8) == 1:  ## orderType 변경 -> 8(manual sell full)
                                print("make order : ", item_code, "SELL FULL(MANUAL)")
                                
                                self.ORDER_SELL(item_code, qty, price)  # ORDER : SELL
                                self.indicate_ordered()         ## INDICATE : ordered

            elif data['autoTrade'] == 1 :
                if self.lock == 0 :
                    self.lock = 1       ## lock
                    step = self.func_GET_db_item(item_code, 1)

                    ## SHOW ##
                    own_count = data['own_count']
                    unit_price = data['unit_price']
                    cur_price = data['cur_price']
                    price_buy = data['price_buy']
                    price_sell = data['price_sell']

                    total_purchase = own_count * unit_price
                    total_evaluation = own_count * cur_price
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

                    self.trans_dict.emit(self.rp_dict)       ## SHOW

                    orderType = self.func_GET_db_item(item_code, 3)

                    # if self.MAKE_ORDER == 1 :
                    if orderType == 4 :
                        if MAKE_ORDER == 1 :
                            qty = self.func_GET_db_item(item_code, 4)       ## DB : qty <- trAmount
                            price = price_buy

                            print("make order : ", item_code, "SELL & BUY(BUY")
                            self.ORDER_BUY(item_code, qty, price)    # ORDER : BUY
                            self.indicate_ordered()         ## INDICATE : ordered

                    else :
                        res = self.judge(percent, step, own_count, price_buy, price_sell, total_purchase, total_evaluation)
                        judge_type = res['judge']

                        if judge_type == 0 :        ## stay
                            print(item_code, "judge : 0")
                            self.lock = 0

                        elif judge_type == 1 :      ## add water
                            print(item_code, "judge : 1")
                            if MAKE_ORDER == 1 :

                                qty = res['buy_qty']
                                price = res['buy_price']

                                # need_price = qty * price

                                # if deposit >= need_price :
                                    # print("CASE : deposit >= total")
                                if self.func_UPDATE_db_item(item_code, 2, 1) == 1:       ## ordered -> 1
                                    if self.func_UPDATE_db_item(item_code, 3, 1) == 1:       ## orderType -> 1
                                        print("make order : ", item_code, "BUY")
                                        
                                        self.ORDER_BUY(item_code, qty, price)    # ORDER : BUY
                                        self.indicate_ordered()         ## INDICATE : ordered

                                # else :
                                #     print("CASE : deposit < total")
                                #     self.lock = 0

                        elif judge_type == 2 :      ## sell & buy
                            print(item_code, "judge : 2")
                            if MAKE_ORDER == 1 :

                                qty = res['sell_qty']
                                price = res['sell_price']

                                if qty == 0 :
                                    print(item_code, "judge : 2 and 3")
                                    qty = own_count
                                    if self.func_UPDATE_db_item(item_code, 2, 1) == 1:      ## ordered 변경 -> 1
                                        if self.func_UPDATE_db_item(item_code, 3, 3) == 1:  ## orderType 변경 -> 3
                                            print("make order : ", item_code, "SELL & BUY(SELL")
                                            
                                            self.ORDER_SELL(item_code, qty, price)  # ORDER : SELL
                                            self.indicate_ordered()         ## INDICATE : ordered

                                elif qty >= 1 :
                                    if self.func_UPDATE_db_item(item_code, 2, 1) == 1:       ## ordered -> 1
                                        if self.func_UPDATE_db_item(item_code, 3, 2) == 1:      ## orderType -> 2
                                            if self.func_UPDATE_db_item(item_code, 4, qty) == 1:    ## 판매수량 -> trAmount
                                                print("make order : ", item_code, "SELL")

                                                self.ORDER_SELL(item_code, qty, price)  # ORDER : SELL
                                                self.indicate_ordered()         ## INDICATE : ordered

                        elif judge_type == 3 :      ## full_sell
                            print(item_code, "judge : 3")
                            if MAKE_ORDER == 1 :

                                qty = res['sell_qty']
                                price = res['sell_price']

                                if self.func_UPDATE_db_item(item_code, 2, 1) == 1:      ## ordered 변경 -> 1
                                    if self.func_UPDATE_db_item(item_code, 3, 3) == 1:  ## orderType 변경 -> 3
                                        print("make order : ", item_code, "SELL")
                                        
                                        self.ORDER_SELL(item_code, qty, price)  # ORDER : SELL
                                        self.indicate_ordered()         ## INDICATE : ordered

                    # elif self.MAKE_ORDER == 0 :
                    #     self.lock = 0
                        
    def indicate_ordered(self) :
        self.rp_dict['ordered'] = 1
        self.rp_dict['seq'] = self.seq
        self.trans_dict.emit(self.rp_dict)      ## INDICATE : ordered

    def get_repeat_cnt(self, trcode, rqname):
        ret = self.worker.dynamicCall("GetRepeatCnt(QString, QString)", trcode, rqname)
        return ret

    

        ################## judgement ###################
    def judge(self, percent, step, own_count, price_buy, price_sell, total_purchase, total_evaluation) :
        res = {}
        # Add Water
        if percent < PER_LOW and step < STEP_LIMIT :
            V = int(price_buy)          # 매도 최우선가
            A = total_purchase          # 총 매입금액
            B = total_evaluation        # 총 평가금액
            T = TAX
            FB = FEE_BUY
            FS = FEE_SELL
            P = GOAL_PER

            buy_qty = math.ceil((B-A-B*T-A*FB-B*FS-A*P) / (V*P + V*T + FB + FS))

            res['judge'] = 1
            res['buy_qty'] = buy_qty
            res['buy_price'] = V

            return res

        # Sell & Buy
        elif percent > PER_HI and step < STEP_LIMIT :
            sell_qty = int(own_count / 2)
            # if sell_qty == 0 :
            #     sell_qty = 1
            price = int(price_sell)

            res['judge'] = 2
            res['sell_qty'] = sell_qty
            res['sell_price'] = price

            return res
        
        # Full Sell
        elif percent > PER_HI and step == STEP_LIMIT :
            sell_qty = own_count
            price = int(price_sell)

            res['judge'] = 3
            res['sell_qty'] = sell_qty
            res['sell_price'] = price

            return res

        # STAY
        else :
            # cur_time = time.time()
            # stay_time = int(self.stay_print_time[code])

            res['judge'] = 0

            return res
            
    ## 매수
    def ORDER_BUY(self, item_code, qty, price) :
        rqname = "RQ_TEST"
        screen_no = "0101"
        acc_no = ACCOUNT
        order_type = 1
        hogagb = "00"
        orgorderno = ""
        order = self.worker.dynamicCall("SendOrder(QString, QString, QString, int, QString, int, int, QString, QString)",
                     [rqname, screen_no, acc_no, order_type, item_code, qty, price, hogagb, orgorderno])
        
        self.func_UPDATE_db_item(item_code, 2, 1)       # 해당 item 의 현재 상태를 Trading으로 변환
        timestamp = self.func_GET_CurrentTime()
        print(timestamp + "ORDER : BUY", item_code, " / ", qty)
    ## 매도
    def ORDER_SELL(self, item_code, qty, price) :
        rqname = "RQ_TEST"
        screen_no = "0101"
        acc_no = ACCOUNT
        order_type = 2
        hogagb = "00"
        orgorderno = ""
        
        order = self.worker.dynamicCall("SendOrder(QString, QString, QString, int, QString, int, int, QString, QString)",
                     [rqname, screen_no, acc_no, order_type, item_code, qty, price, hogagb, orgorderno])
        
        self.func_UPDATE_db_item(item_code, 2, 1)       # oerdered -> 1
        timestamp = self.func_GET_CurrentTime()
        print(timestamp + "ORDER : SELL", item_code, " / ", qty)

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
        print("data INSERTED")
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
        # print("UPDATED")
        return success
    def func_DELETE_db_item(self, code):
        conn = sqlite3.connect("item_status.db")
        cur = conn.cursor()
        sql = "delete from STATUS where code = :CODE"
        cur.execute(sql, {"CODE" : code})
        conn.commit()
        conn.close()
        print("data DELETED")

    def func_GET_CurrentTime(self) :
        year = strftime("%Y", localtime())
        month = strftime("%m", localtime())
        day = strftime("%d", localtime())
        hour = strftime("%H", localtime())
        cmin = strftime("%M", localtime())
        sec = strftime("%S", localtime())

        now = "[" + year + "/" + month +"/" + day + " " + hour + ":" + cmin + ":" + sec + "] "

        return now