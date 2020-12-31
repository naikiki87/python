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
from time import localtime, strftime

STDEV_LIMIT = config.STDEV_LIMIT
MKT_SUM_LIMIT = 5000
VOL_AVERAGE = 100000
VOL_AVERAGE_LOW = 10000
VAL_PRICE_RATIO = 2
SUBS_CNT = 2000

SHOW_SCALE = 5
VOL_FIN_PAGE = 1    # 평균 volume을 구할 표본 수 -> 1 당 10일치

def run():
    print(now(), "[FINDER] [run] START Item Discovering")

    c_now = datetime.datetime.now()

    c_year = c_now.strftime('%Y')
    c_month = c_now.strftime('%m')
    c_day = c_now.strftime('%d')
    c_hour = c_now.strftime('%H')
    c_min = c_now.strftime('%M')
    c_sec = c_now.strftime('%S')

    this_time = c_year + c_month + c_day + c_hour + c_min + c_sec
    
    this_time = "20201216165322"
    print(this_time, type(this_time))
    

    code_df = pd.read_html('http://kind.krx.co.kr/corpgeneral/corpList.do?method=download&searchType=13', header=0)[0] 
    code_df.종목코드 = code_df.종목코드.map('{:06d}'.format) 
    code_df = code_df[['회사명', '종목코드']]
    code_df = code_df.rename(columns={'회사명': 'name', '종목코드': 'code'}) 

    df_last = pd.DataFrame(columns = ['code', 'ratio_min_max', 'mean_vol', 'stdev'])

    df_vol = pd.DataFrame(columns = ['code', 'vol'])
    cnt_code = len(code_df)

    # for i in range(len(code_df)) :
    for i in range(1) :
        print(i)

        try :
            code = code_df.code[i]
            print(code)
            # url = 'http://finance.naver.com/item/sise_day.nhn?code={code}'.format(code=code) 
            url = 'https://finance.naver.com/item/sise_time.nhn?code={code}&thistime={thistime}&page=1'.format(code=code, thistime=thistime)
            df = pd.read_html(url, header=0)[0]

            print(df)

            for page in range(2, VOL_FIN_PAGE + 1) :
                url = 'http://finance.naver.com/item/sise_day.nhn?code={code}&page={page}'.format(code=code, page=page) 
                df = df.append(pd.read_html(url, header=0)[0], ignore_index=True) 
        
            # df = df.rename(columns={'종가':'end', '거래량' : 'vol'})
            df = df.dropna()

            print(df)

            # mean_vol = df.vol.mean()
            # df2 = df[['vol']]

            # min_v = df2.min()
            # max_v = df2.max()

            # # print("min max : ", min_v, max_v)
            # ratio_min_max = round((max_v / min_v), 1)
            # # print("ratio : ", ratio_min_max)

            # norm_df=(df2-df2.min())/(df2.max()-df2.min())
            # norm_df.columns=['norm']
            # stdev = norm_df.norm.std()    # 종가 min-max 정규화 + 표준편차

            # # mkt_sum = get_market_sum(code)

            # if float(ratio_min_max) <= 5 :
            #     # if mean_vol >= 5000 and mean_vol <= 200000 :
            #     # if mkt_sum > 100 and mkt_sum < 1000 :
            #     df_last.loc[len(df_last)] = [code, float(ratio_min_max), int(mean_vol), stdev]

        except :
            pass

    # df_last = df_last.sort_values(by=['ratio_min_max', 'stdev'], axis=0, ascending=[True, True])  # sorting by std(descending)
    # df_last = df_last.reset_index(drop=True, inplace=False)     # re-indexing
    # df_last = df_last.head(100)
    # print(df_last)

    # a_item = []

    # for i in range(len(df_last)) :
    #     a_item.append(df_last.code[i])

    # f_hook = open("target.py",'w')
    # date = "# DATE = " + get_now() + '\n'
    # f_hook.write(date)
    # data = "ITEMS = " + str(a_item)
    # f_hook.write(data)
    # f_hook.close()

    # df_mkt_sum = pd.DataFrame(columns = ['code', 'mkt_sum'])

    # for i in range(len(df_vol)) :
    #     print(i, '/', str(len(df_vol))
    #     try :
    #         code = df_vol.code[i]
    #         mkt_sum = get_market_sum(code)

    #         if mkt_sum < MKT_SUM_LIMIT:
    #             df_mkt_sum.loc[len(df_mkt_sum)] = [code, mkt_sum]

    #     except :
    #         pass

    # item_list = []

    # for i in range(len(df_mkt_sum)) :
    #     item_list.append(df_mkt_sum.code[i])

    # print("itemlist : ", item_list)

def get_market_sum(item_code):
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

def now() :
    return datetime.datetime.now()

def get_now() :
    year = strftime("%Y", localtime())
    month = strftime("%m", localtime())
    day = strftime("%d", localtime())
    hour = strftime("%H", localtime())
    cmin = strftime("%M", localtime())
    sec = strftime("%S", localtime())

    now = "[" + year + "/" + month +"/" + day + " " + hour + ":" + cmin + ":" + sec + "] "

    return now


run()