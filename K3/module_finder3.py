import FinanceDataReader as fdr
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
from datetime import datetime, timedelta, date
import total_items

item_list = total_items.ITEMS
today = date.today()
day_bf_14 = today + timedelta(days=-14)
day_bf_100 = today + timedelta(days=-100)

check_dur = 6

print("Total Items : ", len(item_list))

class Finder(QThread):
    def __init__(self):
        super().__init__()
        self.init_items = []
        self.df_last = pd.DataFrame(columns = ['code', 'ratio_end', 'mean_vol', 'today_vol', 'duration'])
        self.df_last2 = pd.DataFrame(columns = ['code', 'ratio_end', 'mean_vol', 'today_vol', 'duration', 'ratio_100'])
        self.df_last3 = pd.DataFrame(columns = ['code', 'ratio_end', 'mean_vol', 'today_vol', 'duration', 'ratio_100', 'market_sum'])

    def run(self):
        start_time = time.time()
        print("[FINDER 3] [run] START Item Discovering")

        self.check_price1()

    def check_price1(self) :
        for i in range(len(item_list)) :
            if i % 20 == 0 :
                print(i)

            try :
                code = item_list[i]

                df = fdr.DataReader(code, day_bf_14, today)
                df = df.rename(columns={'Close':'end', 'Open':'start', 'High':'high', 'Low':'low', 'Volume' : 'vol'})
                df = df.sort_values(by=['Date'], axis=0, ascending=[False])  # sorting by std(descending)

                mean_vol = int(df.vol.mean())
                today_vol = int(df.vol.iloc[0])

                end2 = int(df.end.iloc[2])
                end1 = int(df.end.iloc[1])
                end0 = int(df.end.iloc[0])

                start2 = int(df.start.iloc[2])
                start1 = int(df.start.iloc[1])
                start0 = int(df.start.iloc[0])

                gap2 = end2 - start2
                gap1 = end1 - start1
                gap0 = end0 - start0
                
                if end1 > end0 :
                    if gap1 < 0 and gap0 < 0 :    
                        self.init_items.append(code)
            except :
                pass

        print("init_items : ", len(self.init_items))
        print(self.init_items)

        self.check_price2()

    def check_price2(self) :
        check_dur = 5
        for i in range(len(self.init_items)) :
            if i % 20 == 0 :
                print(i)

            try :
                code = self.init_items[i]

                df = fdr.DataReader(code, day_bf_14, today)
                df = df.rename(columns={'Close':'end', 'Open':'start', 'High':'high', 'Low':'low', 'Volume' : 'vol'})
                df = df.sort_values(by=['Date'], axis=0, ascending=[False])  # sorting by std(descending)

                mean_vol = int(df.vol.mean())
                today_vol = int(df.vol.iloc[0])

                if mean_vol >= 1000000 and today_vol >= 50000 :
                    end5 = int(df.end.iloc[5])
                    end4 = int(df.end.iloc[4])
                    end3 = int(df.end.iloc[3])
                    end2 = int(df.end.iloc[2])
                    end1 = int(df.end.iloc[1])
                    end0 = int(df.end.iloc[0])

                    start5 = int(df.start.iloc[5])
                    start4 = int(df.start.iloc[4])
                    start3 = int(df.start.iloc[3])
                    start2 = int(df.start.iloc[2])
                    start1 = int(df.start.iloc[1])
                    start0 = int(df.start.iloc[0])

                    gap5 = end5 - start5
                    gap4 = end4 - start4
                    gap3 = end3 - start3
                    gap2 = end2 - start2
                    gap1 = end1 - start1
                    gap0 = end0 - start0

                    ratio_end = round((end0 / end5), 2)     ## 최근 감소율
                    if ratio_end <= 0.95 :
                        self.df_last.loc[len(self.df_last)] = [code, ratio_end, mean_vol, today_vol, check_dur]

            except :
                pass
        
        self.check_price3()

    def check_price3(self) :
        self.df_last = self.df_last.sort_values(by=['duration', 'ratio_end'], axis=0, ascending=[False, True])  # sorting by std(descending)
        self.df_last = self.df_last.reset_index(drop=True, inplace=False)     # re-indexing

        print("before")
        print(self.df_last)

        for i in range(len(self.df_last)) :
            try :
                code = self.df_last.code[i]
                df = fdr.DataReader(code, day_bf_100, today)
                df = df.rename(columns={'Close':'end', 'Open':'start', 'High':'high', 'Low':'low', 'Volume' : 'vol'})
                df = df.sort_values(by=['Date'], axis=0, ascending=[False])  # sorting by std(descending)

                end0 = int(df.end.iloc[0])
                df_end = df[['end']]
                min_price = int(df_end.min())
                max_price = int(df_end.max())

                band = max_price - min_price
                p_pos = end0 - min_price
                ratio_100 = round((p_pos / band), 2)

                if ratio_100 <= 0.7 :
                    ratio_end = self.df_last.ratio_end[i]
                    mean_vol = self.df_last.mean_vol[i]
                    today_vol = self.df_last.today_vol[i]
                    duration = self.df_last.duration[i]
                    self.df_last2.loc[len(self.df_last2)] = [code, ratio_end, mean_vol, today_vol, duration, ratio_100]
            
            except :
                pass

        print("after 1 ", len(self.df_last2))
        print(self.df_last2)

        for i in range(len(self.df_last2)) :
            print(i, "1")
            code = self.df_last2.code[i]
            print(i, "2")
            market_sum = self.get_market_sum(code)

            if market_sum >= 2000 :
                ratio_end = self.df_last2.ratio_end[i]
                mean_vol = self.df_last2.mean_vol[i]
                today_vol = self.df_last2.today_vol[i]
                duration = self.df_last2.duration[i]
                ratio_100 = self.df_last2.ratio_100[i]

                self.df_last3.loc[len(self.df_last3)] = [code, ratio_end, mean_vol, today_vol, duration, ratio_100, market_sum]

        print("after 2 :")
        print(self.df_last3)

        a_item = []
        for i in range(len(self.df_last3)) :
            a_item.append(self.df_last3.code[i])

        final_item = []
        for item in a_item :
            if item not in final_item :
                final_item.append(item)

        f_hook = open("target.py",'w')
        date = "# DATE : " + self.get_now() + '\n'
        f_hook.write(date)
        cnt = "# CNT : " + str(len(final_item)) + '\n'
        f_hook.write(cnt)
        data = "ITEMS = " + str(final_item)
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

    def get_market_sum(self, item_code):
        try :
            print("get market sum : ", item_code)
            cnt_0_digit = 0

            url = "https://finance.naver.com/item/main.nhn?code={}".format(item_code)
            res = requests.get(url)
            soup = BeautifulSoup(res.content, 'lxml')
            result = soup.select('#_market_sum')[0].text.strip()
            result = result.replace(',', '')
            result = result.replace('\t', '')
            result = result.replace('\n', '')

            print("result : ", item_code, result)

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
            print("result2 : ", item_code, market_sum)

            return market_sum
        
        except :
            return 10