import pyupbit
import os
import jwt
import uuid
import hashlib
from urllib.parse import urlencode
import requests
from bs4 import BeautifulSoup

import threading

import func_module

file = open('../../individual/upas.txt', 'r')
s = file.read()
key = s.split('\n')

access_key = key[0]
secret_key = key[1]
upbit = pyupbit.Upbit(access_key, secret_key)

# acc_bal = upbit.get_balances()
# print("ccc : ", acc_bal)
# temp_bal = {}
# total_coin_KRW = 0
# for i in range(0, len(acc_bal[0]), 1) :
#     item = acc_bal[0][i]['currency']
#     if item == "KRW" :
#         balance = float(acc_bal[0][i]['balance'])
#         locked = float(acc_bal[0][i]['locked'])
#         cashKRW = int(balance + locked)
#     else :
#         item_fname = "KRW-" + item
#         cur_price = pyupbit.get_current_price(item_fname)
#         count = acc_bal[0][i]['balance']
#         unit_price = acc_bal[0][i]['avg_buy_price']

#         # print("item : ", item, "count : ", count, "unit : ", unit_price, "price : ", price, type(price))

#     # total_coin_KRW = total_coin_KRW + (float(unit_price) * float(count))
#     total_coin_KRW = total_coin_KRW + (float(cur_price) * float(count))

# print("cashKRW : ", cashKRW)
# print("total Coin : ", int(total_coin_KRW))

# func_module.func_test("aaa")
# aaa = func_module.func_test
# aaa("ppp")

# bbb = func_module.get_cur_price
# a = bbb("KRW-XRP")
# print("a : ", a)


# order_sell = func_module.sell
# order_sell("KRW-SNT")

# order_buy = func_module.buy
# order_buy("KRW-XRP")

# order_addwater = func_module.add_water
# order_addwater("KRW-XRP")

# f_sell = open("trade_log2.txt",'a')
# data = self.get_now() + "[sell volume_ratio_low] item : " + str(item_code) + "volume_ratio : " + str(volume_ratio) + "percent : " + str(percent) + '\n'
# data = "test 1234"
# f_sell.write(data)
# f_sell.close()

# file = open('../../individual/upas.txt', 'r')
# s = file.read()
# row = s.split('\n')

# cnt = 0
# cont = 1

# access_key = row[0]
# secret_key = row[1]
# upbit = pyupbit.Upbit(access_key, secret_key)

# # #### 티커 조회
# tickers = pyupbit.get_tickers()
# print(tickers)

#### 티커 중 KRW 만 추출
# items = []
# for i in range(len(tickers)) :
#     if "KRW" in tickers[i] :
#         items.append(tickers[i])

# print("Count : ", len(items))
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

# ITEM = "KRW-ETH"

#### 10 호가
# orderbook = pyupbit.get_orderbook(ITEM)
# # print("orderbook : ", orderbook)
# bids_asks = orderbook[0]['orderbook_units']
# ask_price = bids_asks[0]['ask_price']
# bid_price = bids_asks[0]['bid_price']
# ask_size = bids_asks[0]['ask_size']
# bid_size = bids_asks[0]['bid_size']

# print("ask : ", ask_price, '/', ask_size)
# print("bid : ", bid_price, '/', bid_size, type(bid_size))
# ratio = round((ask_size / bid_size), 2)
# print("ratio : ", ratio)
# for bid_ask in bids_asks:
#     print(bid_ask)

# price = pyupbit.get_current_price(ITEM)
# print("현재가 : ", price)




#### 잔고조회
# acc_bal = upbit.get_balances()
# print("acc : ", acc_bal)
# for i in range(0, len(acc_bal[0]), 1) :
#     item = acc_bal[0][i]['currency']
#     count = acc_bal[0][i]['balance']
#     unit_price = acc_bal[0][i]['avg_buy_price']
#     print("item : ", item, '/', count, '/', unit_price)


df = pyupbit.get_ohlcv("KRW-BTC", interval="minute30", count=5)
print(df)



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

