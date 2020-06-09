import pandas as pd 
import requests
import threading
import time
from bs4 import BeautifulSoup
from sklearn import preprocessing

start = time.time()

tewt = 100

idx = 0
VOL_FIN_PAGE = 3    # 평균 volume을 구할 표본 수 -> 1 당 10일치
VOL_AVERAGE = 1000000    # 평균 volume filtering 하한치

code_df = pd.read_html('http://kind.krx.co.kr/corpgeneral/corpList.do?method=download&searchType=13', header=0)[0] 
code_df.종목코드 = code_df.종목코드.map('{:06d}'.format) 
code_df = code_df[['회사명', '종목코드']]
code_df = code_df.rename(columns={'회사명': 'name', '종목코드': 'code'}) 

df3 = pd.DataFrame(columns = ['date', 'end'])
df2 = pd.DataFrame(columns = ['end'])
df_last = pd.DataFrame(columns = ['code', 'p_avr', 'std'])

# cnt_code = len(code_df)
cnt_code = 100

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

        for page in range(2, VOL_FIN_PAGE) :
            url = 'http://finance.naver.com/item/sise_day.nhn?code={code}&page={page}'.format(code=code, page=page) 
            df = df.append(pd.read_html(url, header=0)[0], ignore_index=True) 
    
        df = df.rename(columns={'날짜':'date', '종가':'end', '전일비':'gap', '시가':'start', '고가':'high', '저가':'low', '거래량' : 'vol'})
        df = df.dropna()

        df2 = df[['end']]
        mean = df2.end.mean()       # 종가평균

        norm_df=(df2-df2.min())/(df2.max()-df2.min())
        norm_df.columns=['norm']
        std = norm_df.norm.std()    # 종가 min-max 정규화/표준편차

        idx = len(df_last)
        df_last.loc[idx] = [code, mean, std]
    except:
        pass

df_last = df_last.sort_values(by=['std'], axis=0, ascending=False)  # sorting by std(descending)
df_last = df_last.reset_index(drop=True, inplace=False)     # re-indexing
print(df_last)