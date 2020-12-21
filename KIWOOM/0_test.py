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
VOL_FIN_PAGE = 2    # 평균 volume을 구할 표본 수 -> 1 당 10일치

def run():
    print("[FINDER] [run] START Item Discovering")

    code_df = pd.read_html('http://kind.krx.co.kr/corpgeneral/corpList.do?method=download&searchType=13', header=0)[0] 
    code_df.종목코드 = code_df.종목코드.map('{:06d}'.format) 
    code_df = code_df[['회사명', '종목코드']]
    code_df = code_df.rename(columns={'회사명': 'name', '종목코드': 'code'}) 

    # df_last = pd.DataFrame(columns = ['code', 'ratio', 'ratio_2', 'mean_vol', 'ratio_end'])
    df_last = pd.DataFrame(columns = ['code', 'ratio'])

    df_vol = pd.DataFrame(columns = ['code', 'vol'])
    cnt_code = len(code_df)

    # for i in range(len(code_df)) :
    for i in range(10) :
        if i % 100 == 0 :
            print(i)

        try :
            code = code_df.code[i]
            url = 'http://finance.naver.com/item/sise_day.nhn?code={code}'.format(code=code) 
            df = pd.read_html(url, header=0)[0]

            for page in range(2, VOL_FIN_PAGE + 1) :
                url = 'http://finance.naver.com/item/sise_day.nhn?code={code}&page={page}'.format(code=code, page=page) 
                df = df.append(pd.read_html(url, header=0)[0], ignore_index=True) 
        
            # df = df.rename(columns={'종가':'end', '거래량' : 'vol'})
            df = df.dropna()

            # print(df)

            mean_vol = df.거래량.mean()
            df2 = df[['종가']]

            min_v = df2.min()
            max_v = df2.max()

            ratio = round((max_v / min_v), 2)

            df_last.loc[len(df_last)] = [code, ratio]

        except :
            pass

    df_last = df_last.sort_values(by=['ratio'], axis=0, ascending=True)  # sorting by std(descending)
    df_last = df_last.reset_index(drop=True, inplace=False)     # re-indexing
    print(df_last)


run()