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

pd.set_option('display.max_row', 20000)
pd.set_option('display.max_columns', 10000)

STDEV_LIMIT = config.STDEV_LIMIT
MKT_SUM_LIMIT = 5000
VOL_AVERAGE = 100000
VOL_AVERAGE_LOW = 10000
VAL_PRICE_RATIO = 2
SUBS_CNT = 2000

SHOW_SCALE = 5
VOL_FIN_PAGE = 1    # 평균 volume을 구할 표본 수 -> 1 당 10일치

def run():
    start_time = time.time()
    print(now(), "[FINDER] [run] START Item Discovering")

    code_df = pd.read_html('http://kind.krx.co.kr/corpgeneral/corpList.do?method=download&searchType=13', header=0)[0] 
    code_df.종목코드 = code_df.종목코드.map('{:06d}'.format) 
    code_df = code_df[['회사명', '종목코드']]
    code_df = code_df.rename(columns={'회사명': 'name', '종목코드': 'code'}) 

    df_last = pd.DataFrame(columns = ['code', 'ratio_end_deg', 'ratio_min', 'mean_vol', 'today_vol'])

    cnt_code = len(code_df)
    
    # for i in range(len(code_df)) :
    for i in range(1) :
        if i % 10 == 0 :
            print(i)

        try :
            # code = code_df.code[i]
            code = "067000"
            url = 'http://finance.naver.com/item/sise_day.nhn?code={code}'.format(code=code) 
            df = pd.read_html(url, header=0)[0]

            for page in range(2, VOL_FIN_PAGE + 1) :
                url = 'http://finance.naver.com/item/sise_day.nhn?code={code}&page={page}'.format(code=code, page=page) 
                df = df.append(pd.read_html(url, header=0)[0], ignore_index=True) 

            df = df.rename(columns={'종가':'end', '시가':'start', '고가':'high', '저가':'low', '거래량' : 'vol'})
            df = df.dropna()
            print(df)
            mean_vol = int(df.vol.mean())
            today_vol = int(df.vol.iloc[0])

            if today_vol >= 10000 :
                df_end = df[['end']]
                min_price = int(df_end.min())

                end7 = int(df.end.iloc[7])
                end6 = int(df.end.iloc[6])
                end5 = int(df.end.iloc[5])
                end4 = int(df.end.iloc[4])
                end3 = int(df.end.iloc[3])
                end2 = int(df.end.iloc[2])
                end1 = int(df.end.iloc[1])
                end0 = int(df.end.iloc[0])

                start7 = int(df.start.iloc[7])
                start6 = int(df.start.iloc[6])
                start5 = int(df.start.iloc[5])
                start4 = int(df.start.iloc[4])
                start3 = int(df.start.iloc[3])
                start2 = int(df.start.iloc[2])
                start1 = int(df.start.iloc[1])
                start0 = int(df.start.iloc[0])

                low7 = int(df.low.iloc[7])
                low6 = int(df.low.iloc[6])
                low5 = int(df.low.iloc[5])
                low4 = int(df.low.iloc[4])
                low3 = int(df.low.iloc[3])
                low2 = int(df.low.iloc[2])
                low1 = int(df.low.iloc[1])
                low0 = int(df.low.iloc[0])

                high7 = int(df.high.iloc[7])
                high6 = int(df.high.iloc[6])
                high5 = int(df.high.iloc[5])
                high4 = int(df.high.iloc[4])
                high3 = int(df.high.iloc[3])
                high2 = int(df.high.iloc[2])
                high1 = int(df.high.iloc[1])
                high0 = int(df.high.iloc[0])


                gap7 = end7 - start7
                gap6 = end6 - start6
                gap5 = end5 - start5
                gap4 = end4 - start4
                gap3 = end3 - start3
                gap2 = end2 - start2
                gap1 = end1 - start1
                gap0 = end0 - start0

                ratio_end = round((end0 / end6), 2)     ## 최근 감소율
                ratio_end_deg = 0
                if ratio_end <= 0.5 :
                    ratio_end_deg = 5
                elif ratio_end <= 0.6 :
                    ratio_end_deg = 6
                elif ratio_end <= 0.7 :
                    ratio_end_deg = 7
                elif ratio_end <= 0.8 :
                    ratio_end_deg = 8
                elif ratio_end <= 0.9 :
                    ratio_end_deg = 9
                elif ratio_end <= 1 :
                    ratio_end_deg = 10
                elif ratio_end > 1 :
                    ratio_end_deg = 11

                ratio_min = round((end0 / min_price), 2)    ## 최근 한달간 최소값 대비 현재값 비율

                if end5 >= end4 and end4 >= end3 and end3 >= end2 and end2 >= end1 and end1 >= end0 :
                    if gap0 < 0 :
                        df_last.loc[len(df_last)] = [code, ratio_end_deg, ratio_min, mean_vol, today_vol]

        except :
            pass

    df_last = df_last.sort_values(by=['ratio_end_deg', 'ratio_min'], axis=0, ascending=[True, True])  # sorting by std(descending)
    df_last = df_last.reset_index(drop=True, inplace=False)     # re-indexing
    

    filename = "target_items.txt"
    f = open(filename,'w', encoding='utf8')
    sys.stdout = f
    print(df_last)

    sys.stdout = sys.__stdout__
    f.close()

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