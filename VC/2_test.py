import pyupbit
import os
import jwt
import uuid
import hashlib
from urllib.parse import urlencode
import requests
from bs4 import BeautifulSoup

import threading

file = open('../../individual/upas.txt', 'r')
s = file.read()
row = s.split('\n')

cnt = 0
cont = 1

access_key = row[0]
secret_key = row[1]
upbit = pyupbit.Upbit(access_key, secret_key)

# #### 티커 조회
# tickers = pyupbit.get_tickers()
# # print(tickers)

# #### 티커 중 KRW 만 추출
# items = []
# for i in range(len(tickers)) :
#     if "KRW" in tickers[i] :
#         items.append(tickers[i])
# # # print("type : ", type(tickers))
# # # print("len : ", len(tickers))

# print("items : ", items)


#### 현재가 조회
# price = pyupbit.get_current_price("KRW-XRP")
# print(price)

# for i in range(len(items)) :
#     price = pyupbit.get_current_price(items[i])
#     print(i, ' : ', items[i], price)


#### 과거 데이터 조회
# df = pyupbit.get_ohlcv("KRW-BTC", interval="month", count=5)
# print(df)

#### 호가
# orderbook = pyupbit.get_orderbook("KRW-XRP")
# print(orderbook)

ITEM = "KRW-BTC"

#### 10 호가
# orderbook = pyupbit.get_orderbook(ITEM)
# bids_asks = orderbook[0]['orderbook_units']
# ask_price = bids_asks[0]['ask_price']
# bid_price = bids_asks[0]['bid_price']
# # print("aaa : ", ask_price, bid_price)
# # for bid_ask in bids_asks:
# #     print(bid_ask)

# price = pyupbit.get_current_price(ITEM)
# print("현재가 : ", price)




#### 잔고조회
# acc_bal = upbit.get_balances()
# print(acc_bal)
# # print(acc_bal[0])
# for i in range(1, len(acc_bal[0]), 1) :
#     item = acc_bal[0][i]['currency']
#     count = acc_bal[0][i]['balance']
#     unit_price = acc_bal[0][i]['avg_buy_price']
#     print("item : ", item, '/', count, '/', unit_price)



#### 매수
# buy_count = round((49900 / ask_price), 8)
# print("count : ", buy_count)
# ret = upbit.buy_limit_order(ITEM, ask_price, 0.00009188)
# print(ret)

#### 매도
# ret = upbit.sell_limit_order(ITEM, bid_price, 0.00049188)
# print(ret)

#### 주문취소
# ret = upbit.cancel_order('cc52be46-1000-4126-aee7-9bfafb867682')
# print(ret)


#### 주문조회
# access_key = os.environ['UPBIT_OPEN_API_ACCESS_KEY']
# secret_key = os.environ['UPBIT_OPEN_API_SECRET_KEY']
# server_url = os.environ['UPBIT_OPEN_API_SERVER_URL']

# query = {
#     'uuid': '9ca023a5-851b-4fec-9f0a-48cd83c2eaae',
# }
# query_string = urlencode(query).encode()

# m = hashlib.sha512()
# m.update(query_string)
# query_hash = m.hexdigest()

# payload = {
#     'access_key': access_key,
#     'nonce': str(uuid.uuid4()),
#     'query_hash': query_hash,
#     'query_hash_alg': 'SHA512',
# }

# jwt_token = jwt.encode(payload, secret_key).decode('utf-8')
# authorize_token = 'Bearer {}'.format(jwt_token)
# headers = {"Authorization": authorize_token}

# res = requests.get(server_url + "/v1/order", params=query, headers=headers)

# print(res.json())



# print("access key : ", access_key)

# item_code = "005930"
# url = "http://polling.finance.naver.com/api/realtime.nhn?query=SERVICE_ITEM:{}|SERVICE_RECENT_ITEM:{}&_callback=".format(item_code, item_code)
# source = requests.get(url)
# data = source.json()
# # name = data['result']['areas'][0]['datas'][0]['nm']
# value = data['result']['areas'][0]['datas'][0]['nv']

# print("value : ", value)

item_code = "005930"

url = "https://finance.naver.com/item/main.nhn?code=" + item_code
result = requests.get(url)
bs_obj = BeautifulSoup(result.content, "html.parser")
 
no_today = bs_obj.find("p", {"class": "no_today"}) # 태그 p, 속성값 no_today 찾기
blind = no_today.find("span", {"class": "blind"}) # 태그 span, 속성값 blind 찾기
now_price = int(blind.text.strip().replace(',', ''))



print(now_price, type(now_price))

