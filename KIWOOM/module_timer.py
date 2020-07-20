import sys
import time
import datetime
import sqlite3
from PyQt5.QtCore import *
from PyQt5 import QtTest, QtCore, QtWidgets
import pandas as pd 
import requests
import threading
from bs4 import BeautifulSoup

SHOW_SCALE = 5
VOL_FIN_PAGE = 3    # 평균 volume을 구할 표본 수 -> 1 당 10일치
STDEV_LIMIT = 0.25
VOL_AVERAGE = 1000000    # 평균 volume filtering 하한치
MKT_SUM_LIMIT = 3000

class Timer(QThread):
    cur_time = pyqtSignal(dict)
    new_deal = pyqtSignal(dict)
    check_slot = pyqtSignal(int)
    recommend_candidate = pyqtSignal(str)

    def __init__(self):
        super().__init__()
        self.make_db_table()
        self.item_checking = 0

    def run(self):
        temp_time = {}
        test_time = 0
        while True:
            # new_deal = {}
            # new_deal['item_code'] = "035720"
            # new_deal['qty'] = 2
            # # self.new_deal.emit(new_deal)

            now = datetime.datetime.now()
            mkt_open = now.replace(hour=9, minute=0, second=0)
            mkt_close = now.replace(hour=15, minute=20, second=0)
            am10 = now.replace(hour=10, minute=00, second=0)

            item_finding = now.replace(hour=13, minute=53, second=30)

            c_hour = now.strftime('%H')
            c_min = now.strftime('%M')
            c_sec = now.strftime('%S')

            str_time = c_hour + ':' + c_min + ':' + c_sec
            temp_time['time'] = str_time

            if now >= mkt_open and now < mkt_close :
                temp_time['possible'] = 1
                if now >= am10 and c_sec == "00" and self.item_checking == 0 :
                    self.check_slot.emit(1)
            else :
                temp_time['possible'] = 0
                if now >= am10 and c_sec == "00" and self.item_checking == 0 :
                    self.check_slot.emit(1)
            self.cur_time.emit(temp_time)
            test_time = test_time + 1
            time.sleep(1)

    @pyqtSlot(int)
    def res_check_slot(self, data) :
        print("res check slot : ", data)
        if data != 0 :
            self.item_checking = 1
            self.item_discovery()

    def item_discovery(self) :
        code_df = pd.read_html('http://kind.krx.co.kr/corpgeneral/corpList.do?method=download&searchType=13', header=0)[0] 
        code_df.종목코드 = code_df.종목코드.map('{:06d}'.format) 
        code_df = code_df[['회사명', '종목코드']]
        code_df = code_df.rename(columns={'회사명': 'name', '종목코드': 'code'}) 

        df_last = pd.DataFrame(columns = ['code', 'p_avr', 'stdev'])

        # cnt_code = len(code_df)
        cnt_code = 100
        idx = 0

        for i in range(0, cnt_code):
            try:
                if i%50 == 0:
                    complete_ratio = round(i/cnt_code * 100, 1)
                    print()
                    print(str(i) + "/" + str(cnt_code) + "(" + str(complete_ratio) + "%) is completed")
                    print()
                
                code = code_df['code'][i]
                url = 'http://finance.naver.com/item/sise_day.nhn?code={code}'.format(code=code) 
                df = pd.read_html(url, header=0)[0]

                for page in range(2, VOL_FIN_PAGE + 1) :
                    url = 'http://finance.naver.com/item/sise_day.nhn?code={code}&page={page}'.format(code=code, page=page) 
                    df = df.append(pd.read_html(url, header=0)[0], ignore_index=True) 
            
                df = df.rename(columns={'종가':'end', '거래량' : 'vol'})
                df = df.dropna()

                mean_vol = df.vol.mean()

                df2 = df[['end']]
                mean = df2.end.mean()       # 종가평균

                norm_df=(df2-df2.min())/(df2.max()-df2.min())
                norm_df.columns=['norm']
                stdev = norm_df.norm.std()    # 종가 min-max 정규화 + 표준편차

                # if stdev > 0.3 and mean_vol > VOL_AVERAGE :
                if stdev < STDEV_LIMIT and mean_vol > VOL_AVERAGE :
                    idx = len(df_last)
                    df_last.loc[idx] = [code, int(mean), stdev]
            except:
                pass

        df_last = df_last.sort_values(by=['stdev'], axis=0, ascending=True)  # sorting by std(descending)
        df_last = df_last.reset_index(drop=True, inplace=False)     # re-indexing
        print(df_last)

        data_cnt = len(df_last)
        df_last2 = pd.DataFrame(columns = ['code', 'p_avr', 'stdev', 'cur_price', 'price_ratio'])
        idx = 0

        for i in range(data_cnt):
            code = df_last.code[i]
            p_avr = df_last.p_avr[i]
            stdev = df_last.stdev[i]
            cur_price = self.get_cur_price(code)

            price_ratio = round(float(cur_price / p_avr), 2)

            if price_ratio < 0.99 :
                idx = len(df_last2)
                df_last2.loc[idx] = [code, p_avr, stdev, cur_price, price_ratio]

        df_last2 = df_last2.sort_values(by=['price_ratio'], axis=0)  # sorting by stdev(descending)
        df_last2 = df_last2.reset_index(drop=True, inplace=False)     # re-indexing
        print(df_last2)
        print("")

        data_cnt = len(df_last2)
        df_last3 = pd.DataFrame(columns = ['code', 'p_avr', 'stdev', 'cur_price', 'price_ratio', 'mkt_sum'])
        idx = 0

        for i in range(data_cnt):
            try:
                if i % SHOW_SCALE == 0:
                    complete_ratio = round(i/data_cnt * 100, 1)
                    print()
                    print(str(i) + "/" + str(data_cnt) + "(" + str(complete_ratio) + "%) is completed")
                    print()
                
                code = df_last2.code[i]
                mkt_sum = self.get_market_sum(code)

                if mkt_sum > MKT_SUM_LIMIT:
                    idx = len(df_last3)
                    p_avr = df_last2.p_avr[i]
                    stdev = df_last2.stdev[i]
                    cur_price = df_last2.cur_price[i]
                    price_ratio = df_last2.price_ratio[i]

                    df_last3.loc[idx] = [code, p_avr, stdev, cur_price, price_ratio, mkt_sum]
            except:
                pass

        print(df_last3)
        if len(df_last3) != 0 :
            candidate = df_last3.code[0]
            print("candidate : ", candidate)
            self.recommend_candidate.emit(candidate)

        self.item_checking = 0

    def get_cur_price(self, item_code):
        url = "http://polling.finance.naver.com/api/realtime.nhn?query=SERVICE_ITEM:{}|SERVICE_RECENT_ITEM:{}&_callback=".format(item_code, item_code)
        source = requests.get(url)
        data = source.json()
        name = data['result']['areas'][0]['datas'][0]['nm']
        value = data['result']['areas'][0]['datas'][0]['nv']

        return value
    def get_market_sum(self, item_code):
        get_last_3 = 1
        cnt_0_digit = 0

        url = "https://finance.naver.com/item/main.nhn?code={}".format(item_code)
        res = requests.get(url)
        soup = BeautifulSoup(res.content, 'lxml')
        result = soup.select('#_market_sum')[0].text.strip()
        result = result.replace(',', '')
        result = result.replace('\t', '')
        result = result.replace('\n', '')

        nextstr = []
        lensum = len(result)
        ptr = 0
        for k in range(0, lensum):
            if result[k] == '조':
                ptr = k
                break           
            nextstr.append(result[k])
        
        if ptr != 0 :
            cnt_0_digit = 4 - (lensum - (ptr + 1))

            for m in range(0, cnt_0_digit) :
                nextstr.append('0')
            
            for n in range(ptr+1, lensum) :
                nextstr.append(result[n])

        market_sum = int("".join(nextstr))

        return market_sum

    def make_db_table(self) :
        conn = sqlite3.connect("item_status.db")
        cur = conn.cursor()
        sql = "create table if not exists ITEM_LIST (code text, step integer, ordered integer, orderType integer, trAmount integer)"
        cur.execute(sql)
        conn.commit()
        conn.close()