import pandas as pd 
import requests
import threading
import time
from bs4 import BeautifulSoup
from sklearn import preprocessing

def get_cur_price(item_code):
    url = "http://polling.finance.naver.com/api/realtime.nhn?query=SERVICE_ITEM:{}|SERVICE_RECENT_ITEM:{}&_callback=".format(item_code, item_code)
    source = requests.get(url)
    data = source.json()
    name = data['result']['areas'][0]['datas'][0]['nm']
    value = data['result']['areas'][0]['datas'][0]['nv']

    return value

for i in range(50):
    val = get_cur_price("005930")
    print(val)
    time.sleep(1)