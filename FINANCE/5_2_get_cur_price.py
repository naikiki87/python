import pandas as pd 
import requests
import threading
import time
from bs4 import BeautifulSoup

def getData(item_code):
    url = "http://polling.finance.naver.com/api/realtime.nhn?query=SERVICE_ITEM:{}|SERVICE_RECENT_ITEM:{}&_callback=".format(item_code, item_code)
    source = requests.get(url)
    data = source.json()
    name = data['result']['areas'][0]['datas'][0]['nm']
    value = data['result']['areas'][0]['datas'][0]['nv']

    return value

for i in range(10):
    try:
        val = getData("005930")
        print(i, " : ", val)
        time.sleep(1)
    except:
        pass