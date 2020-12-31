import sys
import random
import time
import datetime
import sqlite3
import config
from PyQt5.QtCore import *
from PyQt5 import QtTest, QtCore, QtWidgets
import pandas as pd 
import requests
import threading
from bs4 import BeautifulSoup

STDEV_LIMIT = config.STDEV_LIMIT
VOL_AVERAGE = config.VOL_AVERAGE
MKT_SUM_LIMIT = config.MKT_SUM_LIMIT
SUBS_CNT = config.SUBS_CNT

SHOW_SCALE = 5
VOL_FIN_PAGE = 5    # 평균 volume을 구할 표본 수 -> 1 당 10일치

class Finder(QThread):
    candidate = pyqtSignal(dict)
    alive = pyqtSignal(int)

    def run(self):
        print(self.now(), "[FINDER] [run] START Item Discovering")

        code_df = pd.read_html('http://kind.krx.co.kr/corpgeneral/corpList.do?method=download&searchType=13', header=0)[0] 
        code_df.종목코드 = code_df.종목코드.map('{:06d}'.format) 
        code_df = code_df[['회사명', '종목코드']]
        code_df = code_df.rename(columns={'회사명': 'name', '종목코드': 'code'}) 

        df_last = pd.DataFrame(columns = ['code', 'p_avr', 'stdev'])

        code_df2 = pd.DataFrame(columns={'name', 'code'}) 
        
        subs_cnt = SUBS_CNT
        # subs_cnt = 10

        rand_index = [random.randint(0, len(code_df)) for r in range(subs_cnt)]

        for i in range(subs_cnt) :
            try :
                code_df2.loc[i] = code_df.loc[rand_index[i]]
            except :
                pass

        cnt_code = len(code_df2)
        # cnt_code = 200
        idx = 0

        for i in range(0, cnt_code):
            try:
                if i%50 == 0:
                    complete_ratio = round(i/cnt_code * 100, 1)
                    print("")
                    print(self.now(), "[FINDER]", str(i) + "/" + str(cnt_code) + "(" + str(complete_ratio) + "%) is completed")
                    print("")
                    
                    self.alive.emit(1)
                
                # code = code_df['code'][i]
                code = code_df2['code'][i]
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
        print(self.now(), "[FINDER] Item Finding 1(STDEV + VOLUME) : ", df_last)

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
        print(self.now(), "[FINDER] Item Finding 2(PRICE RATIO) : ", df_last2)

        data_cnt = len(df_last2)
        df_last3 = pd.DataFrame(columns = ['code', 'p_avr', 'stdev', 'cur_price', 'price_ratio', 'mkt_sum'])
        idx = 0

        for i in range(data_cnt):
            try:
                if i % SHOW_SCALE == 0:
                    complete_ratio = round(i/data_cnt * 100, 1)
                    print("")
                    print(self.now(), "[FINDER]", str(i) + "/" + str(data_cnt) + "(" + str(complete_ratio) + "%) is completed")
                    print("")
                    
                    self.alive.emit(1)
                
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

        print(self.now(), "[FINDER] Item Finding 3(MKT SUM) : ", df_last3)

        temp = {}
        if len(df_last3) != 0 :
            item_code = df_last3.code.values.tolist()
            temp['empty'] = 0
            temp['item_code'] = item_code
        elif len(df_last3) == 0 :
            temp['empty'] = 1

        # test_df = pd.DataFrame(columns = ['code', 'p_avr', 'stdev', 'cur_price', 'price_ratio', 'mkt_sum'])
        
        # temp = {}
        # test_df.loc[0] = ["005930", 0, 0, 0, 0, 0]
        # item_code = test_df.code.values.tolist()
        # temp['empty'] = 0
        # temp['item_code'] = item_code

        self.candidate.emit(temp)
        self.alive.emit(2)

    def get_cur_price(self, item_code):
        try :
            url = "http://polling.finance.naver.com/api/realtime.nhn?query=SERVICE_ITEM:{}|SERVICE_RECENT_ITEM:{}&_callback=".format(item_code, item_code)
            source = requests.get(url)
            data = source.json()
            # name = data['result']['areas'][0]['datas'][0]['nm']
            value = data['result']['areas'][0]['datas'][0]['nv']

            # print("now value : ", value)

            return value
        except :
            url = "https://finance.naver.com/item/main.nhn?code=" + item_code
            result = requests.get(url)
            bs_obj = BeautifulSoup(result.content, "html.parser")
            
            no_today = bs_obj.find("p", {"class": "no_today"}) # 태그 p, 속성값 no_today 찾기
            blind = no_today.find("span", {"class": "blind"}) # 태그 span, 속성값 blind 찾기
            now_price = int(blind.text.strip().replace(',', ''))

            # print("now price : ", now_price)

            return now_price

    def get_market_sum(self, item_code):
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

    def now(self) :
        return datetime.datetime.now()