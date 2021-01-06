import pyupbit
import os
import jwt
import uuid
import hashlib
from urllib.parse import urlencode
import requests
from bs4 import BeautifulSoup
from time import sleep
import pandas as pd

import threading

import func_module

file = open('../../individual/upas.txt', 'r')
s = file.read()
key = s.split('\n')

access_key = key[0]
secret_key = key[1]
upbit = pyupbit.Upbit(access_key, secret_key)

# # #### 티커 조회
tickers = pyupbit.get_tickers()
# print(tickers)

### 티커 중 KRW 만 추출
items = []
for i in range(len(tickers)) :
    if "KRW" in tickers[i] :
        items.append(tickers[i])

# print("Count : ", len(items))
# print("items : ", items)

df_items = pd.DataFrame(columns = ['item', 'duration', 'down_ratio'])

def find_item(duration) :
    global df_items
    print("duration : ", duration)

    for i in range(len(items)) :
    # for i in range(1) :
        print(i, '/', len(items))
        
        sleep(0.1)
        item = items[i]
        print(item)
        df = pyupbit.get_ohlcv(item, interval="minute30", count=5)
        c0 = df.close[0]
        c1 = df.close[1]
        c2 = df.close[2]
        c3 = df.close[3]
        c4 = df.close[4]

        print(df)
        
        if duration == 4 :
            if c0 > c1 and c1 > c2 and c2 > c3 and c3 > c4 :
                down_ratio = round((((c4-c0)/c0) * 100), 2)
                df_items.loc[len(df_items)] = [item, duration, down_ratio]
        
        elif duration == 3 :
            if c1 > c2 and c2 > c3 and c3 > c4 :
                is_there = 0
                for j in range(len(df_items)) :
                    gi_item = df_items.item[j]
                    if item == gi_item :
                        is_there = 1
                
                if is_there == 0 :
                    down_ratio = round((((c4-c1)/c1) * 100), 2)
                    df_items.loc[len(df_items)] = [item, duration, down_ratio]

        elif duration == 2 :
            if c2 > c3 and c3 > c4 :
                is_there = 0
                for j in range(len(df_items)) :
                    gi_item = df_items.item[j]
                    if item == gi_item :
                        is_there = 1
                
                if is_there == 0 :
                    down_ratio = round((((c4-c2)/c2) * 100), 2)
                    df_items.loc[len(df_items)] = [item, duration, down_ratio]

    if duration > 3 :
        duration = duration - 1
        find_item(duration)
    
    else :
        df_items = df_items.sort_values(by=['duration', 'down_ratio'], axis=0, ascending=[False, True])  # sorting by std(descending)
        df_items = df_items.reset_index(drop=True, inplace=False)     # re-indexing

        print(df_items)

find_item(4)    

