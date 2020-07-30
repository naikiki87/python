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
VOL_FIN_PAGE = 5    # 평균 volume을 구할 표본 수 -> 1 당 10일치
STDEV_LIMIT = 0.25
VOL_AVERAGE = 1000000    # 평균 volume filtering 하한치
MKT_SUM_LIMIT = 3000

class Finder(QThread):
    candidate = pyqtSignal(dict)
    alive = pyqtSignal(int)

    def run(self):
        print("-- [START] Item Discovering --")

        code_df = pd.read_html('http://kind.krx.co.kr/corpgeneral/corpList.do?method=download&searchType=13', header=0)[0] 
        code_df.종목코드 = code_df.종목코드.map('{:06d}'.format) 
        code_df = code_df[['회사명', '종목코드']]
        code_df = code_df.rename(columns={'회사명': 'name', '종목코드': 'code'}) 

        df_last = pd.DataFrame(columns = ['code', 'p_avr', 'stdev'])

        cnt_code = len(code_df)
        # cnt_code = 1000
        idx = 0

        for i in range(0, cnt_code):
            try:
                if i%50 == 0:
                    complete_ratio = round(i/cnt_code * 100, 1)
                    print()
                    print(str(i) + "/" + str(cnt_code) + "(" + str(complete_ratio) + "%) is completed")
                    print()
                    
                    self.alive.emit(1)
                
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

        temp = {}
        if len(df_last3) != 0 :
            item_code = df_last3.code.values.tolist()
            temp['empty'] = 0
            temp['item_code'] = item_code
        elif len(df_last3) == 0 :
            temp['empty'] = 1
        print("send candidate")
        self.candidate.emit(temp)

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