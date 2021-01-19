import requests
import threading
from bs4 import BeautifulSoup

# def get_cur_price(item_code):
#     try :
#         url = "http://polling.finance.naver.com/api/realtime.nhn?query=SERVICE_ITEM:{}|SERVICE_RECENT_ITEM:{}&_callback=".format(item_code, item_code)
#         source = requests.get(url)
#         data = source.json()
#         value = data['result']['areas'][0]['datas'][0]['nv']

#         return value

#     except :
#         return 1

# print(get_cur_price("005930"))
item_code = "005930"
url = "http://polling.finance.naver.com/api/realtime.nhn?query=SERVICE_ITEM:{}|SERVICE_RECENT_ITEM:{}&_callback=".format(item_code, item_code)
source = requests.get(url)
print(source)
# data = source.json()
# value = data['result']['areas'][0]['datas'][0]['nv']