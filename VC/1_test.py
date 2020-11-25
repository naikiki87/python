import pyupbit
import os
import jwt
import uuid
import hashlib
from urllib.parse import urlencode
import requests

import threading

file = open('../../individual/upas.txt', 'r')
s = file.read()
row = s.split('\n')

cnt = 0
cont = 1

access_key = row[0]
secret_key = row[1]
upbit = pyupbit.Upbit(access_key, secret_key)

def func_test() :
    print("import func test")

class ThreadJob(threading.Thread):
    def __init__(self,callback,event,interval):
        self.callback = callback
        self.event = event
        self.interval = interval
        super(ThreadJob,self).__init__()

    def run(self):
        global cnt

        while not self.event.wait(self.interval):
            print("cnt : ", cnt)
            cnt = cnt + 1
            self.callback()

event = threading.Event()

def foo():
    orderbook = pyupbit.get_orderbook("KRW-XRP")
    bids_asks = orderbook[0]['orderbook_units']
    ask_price = bids_asks[0]['ask_price']
    bid_price = bids_asks[0]['bid_price']

    # percent = round((((bid_price - unit_price) / unit_price), 4) * 100)
    percent = round((((bid_price - unit_price) / unit_price) * 100), 2)
    print("현재가 : ", bid_price, "percent : ", percent)



acc_bal = upbit.get_balances()
unit_price = float(acc_bal[0][1]['avg_buy_price'])
count = acc_bal[0][1]['balance']
print("unit : ", unit_price, type(unit_price), count)

k = ThreadJob(foo,event,2)
# k.start()



#### 티커 조회
# tickers = pyupbit.get_tickers()
# print(tickers)

#### 티커 중 KRW 만 추출
# items = []
# for i in range(len(tickers)) :
#     if "KRW" in tickers[i] :
#         items.append(tickers[i])
# # print("type : ", type(tickers))
# # print("len : ", len(tickers))


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

#### 10 호가
# orderbook = pyupbit.get_orderbook("KRW-XRP")
# bids_asks = orderbook[0]['orderbook_units']
# ask_price = bids_asks[0]['ask_price']
# bid_price = bids_asks[0]['bid_price']
# print("aaa : ", ask_price, bid_price)
# for bid_ask in bids_asks:
#     print(bid_ask)

# price = pyupbit.get_current_price("KRW-BTC")
# print("현재가 : ", price)




#### 잔고조회
# acc_bal = upbit.get_balances()
# # print(upbit.get_balances())
# # print("balance : ", acc_bal)
# # print("len : ", len(acc_bal))
# # print(acc_bal[0])
# # print("len2 : ", len(acc_bal[0]))
# for i in range(1, len(acc_bal[0]), 1) :
#     item = acc_bal[0][i]['currency']
#     count = acc_bal[0][i]['balance']
#     unit_price = acc_bal[0][i]['avg_buy_price']
#     print("item : ", item, '/', count, '/', unit_price)



#### 매수
buy_count = round((5000 / ask_price), 8)
print("count : ", buy_count)
ret = upbit.buy_limit_order("KRW-XRP", ask_price, buy_count)
print(ret)

#### 매도
# ret = upbit.sell_limit_order("KRW-XRP", 1000, 20)
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