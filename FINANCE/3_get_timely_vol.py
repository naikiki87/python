import pandas as pd 
import requests
import threading
import time
from bs4 import BeautifulSoup
import matplotlib.pyplot as plt
import matplotlib as mpl
from matplotlib import font_manager, rc

df = pd.DataFrame()

for page in range(1, 39): 
    pg_url = "https://finance.naver.com/item/sise_time.nhn?code=005930&thistime=20200525153020&page={page}".format(page=page)

    df = df.append(pd.read_html(pg_url, header=0)[0], ignore_index=True) 
    
# df.dropna()를 이용해 결측값 있는 행 제거     
df = df.dropna()
df = df.rename(columns={'거래량' : 'volume'})
df = df.sort_values(by=['volume'], axis=0)
print(df)

arHello = df['volume'][:]

print(arHello)