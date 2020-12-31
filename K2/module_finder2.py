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

class Finder(QThread):
    def run(self):
        start_time = time.time()
        print("[FINDER 2] [run] START Item Discovering")

        code_df = pd.read_html('http://kind.krx.co.kr/corpgeneral/corpList.do?method=download&searchType=13', header=0)[0] 
        code_df.종목코드 = code_df.종목코드.map('{:06d}'.format) 
        code_df = code_df[['회사명', '종목코드']]
        code_df = code_df.rename(columns={'회사명': 'name', '종목코드': 'code'}) 

        df_last = pd.DataFrame(columns = ['code', 'ratio_end_deg', 'ratio_min', 'mean_vol', 'today_vol'])

        cnt_code = len(code_df)
        
        for i in range(len(code_df)) :
            if i % 10 == 0 :
                print(i)

            try :
                code = code_df.code[i]
                url = 'http://finance.naver.com/item/sise_day.nhn?code={code}'.format(code=code) 
                df = pd.read_html(url, header=0)[0]
                df = df.rename(columns={'종가':'end', '시가':'start', '고가':'high', '저가':'low', '거래량' : 'vol'})
                df = df.dropna()

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

                    gap7 = end7 - start7
                    gap6 = end6 - start6
                    gap5 = end5 - start5
                    gap4 = end4 - start4
                    gap3 = end3 - start3
                    gap2 = end2 - start2
                    gap1 = end1 - start1
                    gap0 = end0 - start0

                    ratio_end = round((end0 / end4), 2)     ## 최근 감소율
                    ratio_end_deg = round(ratio_end, 1)

                    ratio_min = round((end0 / min_price), 2)    ## 최근 한달간 최소값 대비 현재값 비율

                    if end3 >= end2 and end2 >= end1 and end1 >= end0 :
                        if gap3 < 0 and gap2 < 0 and gap1 < 0 and gap0 < 0 :
                            df_last.loc[len(df_last)] = [code, ratio_end_deg, ratio_min, mean_vol, today_vol]

            except :
                pass

        df_last = df_last.sort_values(by=['ratio_end_deg', 'ratio_min'], axis=0, ascending=[True, True])  # sorting by std(descending)
        df_last = df_last.reset_index(drop=True, inplace=False)     # re-indexing

        a_item = []

        for i in range(len(df_last)) :
            a_item.append(df_last.code[i])

        f_hook = open("target.py",'w')
        date = "# DATE = " + self.get_now() + '\n'
        f_hook.write(date)
        data = "ITEMS = " + str(a_item)
        f_hook.write(data)
        f_hook.close()

    def get_now(self) :
        year = strftime("%Y", localtime())
        month = strftime("%m", localtime())
        day = strftime("%d", localtime())
        hour = strftime("%H", localtime())
        cmin = strftime("%M", localtime())
        sec = strftime("%S", localtime())

        now = "[" + year + "/" + month +"/" + day + " " + hour + ":" + cmin + ":" + sec + "] "

        return now