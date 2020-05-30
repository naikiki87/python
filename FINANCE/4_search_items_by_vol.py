import pandas as pd 
import requests
import threading
import time
from bs4 import BeautifulSoup

idx = 0

code_df = pd.read_html('http://kind.krx.co.kr/corpgeneral/corpList.do?method=download&searchType=13', header=0)[0] 
code_df.종목코드 = code_df.종목코드.map('{:06d}'.format) 
code_df = code_df[['회사명', '종목코드']]
code_df = code_df.rename(columns={'회사명': 'name', '종목코드': 'code'}) 

df2 = pd.DataFrame(columns = ['code', 'D', 'D-1'])

codecount = len(code_df)
# codecount = 1000

for i in range(0, codecount):
    try:
        if i%50 == 0:
            complete_ratio = round(i/codecount * 100, 1)
            print()
            print(str(i) + "/" + str(codecount) + "(" + str(complete_ratio) + "%) is completed")
            print()
        
        code = code_df['code'][i]

        # print(code)

        url = 'http://finance.naver.com/item/sise_day.nhn?code={code}'.format(code=code) 
        df = pd.read_html(url, header=0)[0]
        df = df.dropna()
        df = df.rename(columns={'날짜':'date', '종가':'end', '전일비':'gap', '시가':'start', '고가':'high', '저가':'low', '거래량' : 'vol'})
        # print(df)

        today_vol = df.iloc[0]['vol']
        day1before_vol = df.iloc[1]['vol']
        day2before_vol = df.iloc[2]['vol']
        
        today_start = df.iloc[0]['start']
        day1before_start = df.iloc[1]['start']
        day2before_start = df.iloc[2]['start']

        today_end = df.iloc[0]['end']
        day1before_end = df.iloc[1]['end']
        day2before_end = df.iloc[2]['end']

        today_posneg = today_end - today_start
        day1before_posneg = day1before_end - day1before_start
        day2before_posneg = day2before_end - day2before_start

        # print(today_posneg)
        # print(day1before_posneg)
        # print(day2before_posneg)

        today_ratio = today_vol/day1before_vol
        day1before_ratio = day1before_vol/day2before_vol

        if day1before_vol > 500000:
            if day1before_ratio > 5:    # 어제 거래량이 그저께 거래량보다 급등한 경우
                if today_ratio > 0.7 and today_ratio<1.5:   # 금일 거래량이 어제 거래량에 상당한 수준
                    if day1before_posneg > 0 :  # 어제 양봉일 경우
                        idx = len(df2) + 1
                        df2.loc[idx] = [code, today_ratio, day1before_ratio]
    except:
        pass

print(df2)

# df2.to_csv('itemfindresult.csv')
