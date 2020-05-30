import pandas as pd 
import requests
import threading
import time
from bs4 import BeautifulSoup
from mlxtend.preprocessing import TransactionEncoder
from mlxtend.frequent_patterns import apriori
from mlxtend.frequent_patterns import association_rules

url = "https://finance.naver.com/item/sise_time.nhn?code=005930&thistime=20200526153000"

df = pd.read_html(url, header=0)[0]



for page in range(1, 50): 
    pg_url = '{url}&page={page}'.format(url=url, page=page) 

    try:
        df = df.append(pd.read_html(pg_url, header=0)[0], ignore_index=True) 
    except:
        pass
    
df = df.dropna()
df = df.rename(columns={'체결가':'val'})

df2 = pd.DataFrame(columns = ['id', 'val'])
df2 = df.val
df2.loc[1] = df.val[1]

print(df2)