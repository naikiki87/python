import sys
import time
import pandas as pd
import sqlite3
import math

from PyQt5.QtWidgets import *
from PyQt5.QAxContainer import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5 import QtTest, QtCore

TAX = 0.0025
FEE_BUY = 0.0035
FEE_SELL = 0.0035
GOAL_PER = -0.01
STEP_LIMIT = 5
PER_LOW = -1.5
PER_HI = 1
MAKE_ORDER = 0
ACCOUNT = "8137639811"
PASSWORD = "6458"

class Worker(QThread):
    connected = 0
    data_from_thread = pyqtSignal(int)
    trans_dict = pyqtSignal(dict)
    th_con = pyqtSignal(int)
    delete_item = pyqtSignal(str)

    def __init__(self, seq):
        super().__init__()
        self.seq = seq
        self.worker = QAxWidget()
        self.worker.setControl("KHOPENAPI.KHOpenAPICtrl.1")
        self.worker.dynamicCall("CommConnect()")

        self.worker.OnEventConnect.connect(self.event_connect)
        self.worker.OnReceiveTrData.connect(self.receive_tr_data)
        self.worker.OnReceiveChejanData.connect(self.func_RECEIVE_Chejan_data)

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
        while True:
            try:
                print("con : ", self.connected)
                if self.connected == 1:
                    # self.th_con.emit(1)
                    break
                time.sleep(1)
            except:
                pass
    
    @pyqtSlot("PyQt_PyObject")
    def data_from_main(self, data) :
        print(self.seq, " : ", data)

    # @pyqtSlot("PyQt_PyObject")
    @pyqtSlot(dict)
    def dict_from_main(self, data) :
        item_code = data['item_code']
        if self.lock == 0 :
            self.lock = 1       ## lock
            if self.func_GET_db_item(item_code, 1) == "none" :      ## db init
                self.func_INSERT_db_item(item_code, 0, 0, 0, 0)       # db initialize
                self.lock = 0
            else :
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

                self.rp_dict['lock'] = 1
                self.rp_dict['total_purchase'] = total_purchase
                self.rp_dict['total_evaluation'] = total_evaluation
                self.rp_dict['temp_total'] = temp_total
                self.rp_dict['total_fee'] = total_fee
                self.rp_dict['total_sum'] = total_sum
                self.rp_dict['percent'] = percent
                self.rp_dict['step'] = step
                
                self.rp_dict['seq'] = self.seq

                orderType = self.func_GET_db_item(item_code, 3)

                if orderType == 4 :
                    buy_qty = self.func_GET_db_item(item_code, 4)
                    buy_price = price_buy

                    if self.func_UPDATE_db_item(item_code, 2, 1) == 1:       ## ordered 변경(-> 1)
                        if self.func_UPDATE_db_item(item_code, 3, 4) == 1:       ## orderType -> 4
                            if MAKE_ORDER == 1:
                                print("make order : ", item_code, "BUY")
                                self.func_ORDER_BUY_2(item_code, buy_qty, buy_price)    # make order

                else :
                    res = self.judge(percent, step, own_count, price_buy, price_sell, total_purchase, total_evaluation)
                    judge_type = res['judge']

                    if judge_type == 0 :        ## stay
                        print(item_code, "judge : 0")
                        self.rp_dict['lock'] = 0
                        self.lock = 0
                        self.trans_dict.emit(self.rp_dict)

                    elif judge_type == 1 :      ## add water
                        print(item_code, "judge : 1")
                        self.trans_dict.emit(self.rp_dict)      ## show status

                        buy_qty = res['buy_qty']
                        buy_price = res['buy_price']

                        if self.func_UPDATE_db_item(item_code, 2, 1) == 1:       ## ordered 변경(-> 1)
                            if self.func_UPDATE_db_item(item_code, 3, 1) == 1:       ## orderType을 물타기(1) 로 변경
                                if MAKE_ORDER == 1:
                                    print("make order : ", item_code, "BUY")
                                    self.func_ORDER_BUY_2(item_code, buy_qty, buy_price)    # make order

                    elif judge_type == 2 :      ## sell & buy
                        print(item_code, "judge : 2")
                        self.trans_dict.emit(self.rp_dict)

                        sell_qty = res['sell_qty']
                        price = res['sell_price']

                        if self.func_UPDATE_db_item(item_code, 2, 1) == 1:       ## ordered -> 1
                            if self.func_UPDATE_db_item(item_code, 3, 2) == 1:      ## orderType -> 2
                                if self.func_UPDATE_db_item(item_code, 4, sell_qty) == 1:    ## 판매수량 -> trAmount
                                    if MAKE_ORDER == 1:
                                        print("make order : ", item_code, "SELL")
                                        self.func_ORDER_SELL_2(item_code, sell_qty, price)

                    elif judge_type == 3 :      ## full_sell
                        print(item_code, "judge : 3")
                        self.trans_dict.emit(self.rp_dict)

                        sell_qty = res['sell_qty']
                        price = res['sell_price']

                        if self.func_UPDATE_db_item(item_code, 2, 1) == 1:      ## ordered 변경 -> 1
                            if self.func_UPDATE_db_item(item_code, 3, 3) == 1:  ## orderType 변경 -> 3
                                if MAKE_ORDER == 1:
                                    print("make order : ", item_code, "SELL")
                                    self.func_ORDER_SELL_2(item_code, sell_qty, price)


    def receive_tr_data(self, screen_no, rqname, trcode, recordname, prev_next, data_len, err_code, msg1, msg2):
        if rqname == "opt10001_req":
            print(self.seq, " data received", rqname)
    def get_repeat_cnt(self, trcode, rqname):
        ret = self.worker.dynamicCall("GetRepeatCnt(QString, QString)", trcode, rqname)
        return ret

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
        conn = sqlite3.connect("item_status.db")
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
            
    ## 매수 ##
    def func_ORDER_BUY_2(self, item_code, qty, price) :
        timestamp = self.func_GET_CurrentTime()
        self.text_edit.append(timestamp + "ORDER : BUY")

        rqname = "RQ_TEST"
        screen_no = "0101"
        acc_no = ACCOUNT
        order_type = 1
        hogagb = "00"
        orgorderno = ""
        order = self.kiwoom.dynamicCall("SendOrder(QString, QString, QString, int, QString, int, int, QString, QString)",
                     [rqname, screen_no, acc_no, order_type, item_code, qty, price, hogagb, orgorderno])
        
        today = self.func_GET_Today()
        self.func_GET_Ordering(today)
        self.func_UPDATE_db_item(item_code, 2, 1)       # 해당 item 의 현재 상태를 Trading으로 변환

    def func_ORDER_SELL_2(self, item_code, qty, price) :
        timestamp = self.func_GET_CurrentTime()
        self.text_edit.append(timestamp + "ORDER : SELL")
        
        rqname = "RQ_TEST"
        screen_no = "0101"
        acc_no = ACCOUNT
        order_type = 2
        hogagb = "00"
        orgorderno = ""
        
        order = self.kiwoom.dynamicCall("SendOrder(QString, QString, QString, int, QString, int, int, QString, QString)",
                     [rqname, screen_no, acc_no, order_type, item_code, qty, price, hogagb, orgorderno])
        
        self.func_UPDATE_db_item(item_code, 2, 1)       # oerdered -> 1

    def func_GET_Chejan_data(self, fid):
        ret = self.kiwoom.dynamicCall("GetChejanData(int)", fid)
        return ret
    def func_RECEIVE_Chejan_data(self, gubun, item_cnt, fid_list):
        order_id = item_code = item_name = trade_price = trade_amount = remained = trade_time = 'n'
        if gubun == "0" :       
            order_id = self.func_GET_Chejan_data(9203)      # 주문번호
            item_code = self.func_GET_Chejan_data(9001)     # 종목코드
            item_name = self.func_GET_Chejan_data(302)      # 종목명
            trade_amount = self.func_GET_Chejan_data(911)   # 체결량
            remained = self.func_GET_Chejan_data(902)       # 미체결
            trade_time = self.func_GET_Chejan_data(908)      # 주문체결시간

            # 데이터가 여러번 표시되는 것이 아니라 다 받은 후 일괄로 처리되기 위함
            if remained == '0':         # 체결시
                item_code = item_code.replace('A', '').strip()
                step = self.func_GET_db_item(item_code, 1)
                #### orderType 검사
                orderType = self.func_GET_db_item(item_code, 3)

                if orderType == 1 :         # add water
                    print("chejan : add water")
                    if self.func_UPDATE_db_item(item_code, 2, 0) == 1:       # ordered -> 0
                        if self.func_UPDATE_db_item(item_code, 3, 0) == 1:       # orderType -> 0
                            new_step = step + 1
                            if self.func_UPDATE_db_item(item_code, 1, new_step) == 1:
                                self.lock = 0           # unlock

                elif orderType == 2 :       # sell & buy 중 sell 완료
                    print("chejan : sell&buy - sell")
                    if self.func_UPDATE_db_item(item_code, 3, 4) == 1:       # orderType -> 4
                        # self.trans_dict.emit(self.rp_dict)
                        self.lock = 0           ## unlock

                elif orderType == 3 :       # full sell
                    print("chejan : full sell")
                    self.func_DELETE_db_item(item_code)
                    self.delete_item.emit(item_code)        ## 감시대상에서 삭제
                    self.lock = 0

                elif orderType == 4 :       # sell & buy 중 buy 완료
                    print("chejan : sell&buy - buy")
                    if self.func_UPDATE_db_item(item_code, 2, 0) == 1:      # ordered -> 0
                        if self.func_UPDATE_db_item(item_code, 3, 0) == 1:  # orderType -> 0
                            if self.func_UPDATE_db_item(item_code, 4, 0) == 1:       # trAmount -> 0
                                self.lock = 0
