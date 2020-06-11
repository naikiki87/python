import pandas as pd 
import requests
import threading
import time
from time import localtime, strftime
from bs4 import BeautifulSoup
from sklearn import preprocessing
import datetime

pd.set_option('display.max_rows', 500)
pd.set_option('display.max_columns', 500)
pd.set_option('display.width', 1000)

VOL_FIN_PAGE = 3

def get_cur_price(item_code):
    url = "http://polling.finance.naver.com/api/realtime.nhn?query=SERVICE_ITEM:{}|SERVICE_RECENT_ITEM:{}&_callback=".format(item_code, item_code)
    source = requests.get(url)
    data = source.json()
    name = data['result']['areas'][0]['datas'][0]['nm']
    value = data['result']['areas'][0]['datas'][0]['nv']

    return value

year = strftime("%Y", localtime())
month = strftime("%m", localtime())
day = strftime("%d", localtime())
hour = strftime("%H", localtime())
cmin = strftime("%M", localtime())
sec = strftime("%S", localtime())
# now = year + month + day + hour + cmin + sec
now = year + month + day + hour + cmin

# code = "005930"

code_df = pd.read_html('http://kind.krx.co.kr/corpgeneral/corpList.do?method=download&searchType=13', header=0)[0] 
code_df.종목코드 = code_df.종목코드.map('{:06d}'.format) 
code_df = code_df[['회사명', '종목코드']]
code_df = code_df.rename(columns={'회사명': 'name', '종목코드': 'code'}) 

df_last = pd.DataFrame(columns = ['code', 'stdev', 'm_price', 'c_price', 'status'])
idx = 0

# cnt_code = len(code_df)
cnt_code = 10000
is_continue = 1

for i in range(cnt_code):
# while True:
# while is_continue:
    try:
        if i%50 == 0:
            complete_ratio = round(i/cnt_code * 100, 1)
            print()
            print(str(i) + "/" + str(cnt_code) + "(" + str(complete_ratio) + "%) is completed")
            print()

        # code = code_df['code'][i]
        code = "002360"

        url = "https://finance.naver.com/item/sise_time.nhn?code={code}&page=1&thistime={now}".format(code = code, now = now)
        df = pd.read_html(url, header=0)[0]

        for page in range(2, VOL_FIN_PAGE + 1) :
            url = "https://finance.naver.com/item/sise_time.nhn?code={code}&page={page}&thistime={now}".format(code = code, page = page, now = now)
            df = df.append(pd.read_html(url, header=0)[0], ignore_index=True) 

        df = df.rename(columns={'체결시각':'time', '체결가':'price', '전일비':'gap', '매도':'sell', '매수':'buy', '거래량' : 'vol', '변동량' : 'delta'})
        df = df.dropna()
        df = df.reset_index(drop=True, inplace=False)     # re-indexing

        df2 = df[['time', 'price']]
        temp_df = df[['price']]
        norm_df=(temp_df-temp_df.min())/(temp_df.max()-temp_df.min())
        norm_df.columns=['norm']

        res = pd.concat([df2, norm_df], axis=1)

        # print(res)

        mean_price = res.price.mean()
        stdev = res.norm.std()
        now_price = get_cur_price(code)

        if stdev > 0.2:
            if mean_price > now_price:
                status = -1
                
            else:
                status = 1

        else:
            status = 0
        
        idx = len(df_last)
        df_last.loc[idx] = [code, stdev, mean_price, now_price, status]
        print(df_last)
        time.sleep(5)

    except:
        pass

# print(df_last)