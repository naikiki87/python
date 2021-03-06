import pyupbit
import config
from time import localtime, strftime

NEW_BUY_AMT = config.NEW_BUY_AMT
# NEW_BUY_AMT = 5000
ADD_WATER_PER = config.ADD_WATER_PER

file = open('../../individual/upas.txt', 'r')
s = file.read()
row = s.split('\n')
access_key = row[0]
secret_key = row[1]
upbit = pyupbit.Upbit(access_key, secret_key)



def func_test(item) :
    print("import func test : ", item)

def get_cur_price(item) :
    price = pyupbit.get_current_price(item)
    print(price)

    return price

def sell(target_item) :
    print("func module sell : ", target_item)
    orderbook = pyupbit.get_orderbook(target_item)
    bids_asks = orderbook[0]['orderbook_units']
    ask_price = bids_asks[0]['ask_price']
    bid_price = bids_asks[0]['bid_price']

    acc_bal = upbit.get_balances()

    try :
        for i in range(0, len(acc_bal[0]), 1) :
            item = acc_bal[0][i]['currency']
            if item != "KRW" and item in target_item :
                qty = float(acc_bal[0][i]['balance'])
                unit_price = float(acc_bal[0][i]['avg_buy_price'])
                locked = float(acc_bal[0][i]['locked'])

        ret = upbit.sell_limit_order(target_item, bid_price, qty)
        print("[sell] item : ", target_item, "/ price : ", bid_price, "/ Qty : ", qty)
        # print("time : ", ret)

        
        
    except :
        pass

def buy(item) :
    try :
        print("func module buy : ", item)
        orderbook = pyupbit.get_orderbook(item)
        bids_asks = orderbook[0]['orderbook_units']
        ask_price = bids_asks[0]['ask_price']
        bid_price = bids_asks[0]['bid_price']

        qty = round((NEW_BUY_AMT / ask_price), 8)
        
        ret = upbit.buy_limit_order(item, ask_price, qty)
        print("[New Buy] item : ", item, "/ price : ", ask_price, "/ qty : ", qty)
        # print(ret)
    except :
        pass

def add_water(target_item) :
    try :
        orderbook = pyupbit.get_orderbook(target_item)
        bids_asks = orderbook[0]['orderbook_units']
        ask_price = bids_asks[0]['ask_price']
        bid_price = bids_asks[0]['bid_price']

        acc_bal = upbit.get_balances()

        for i in range(0, len(acc_bal[0]), 1) :
            item = acc_bal[0][i]['currency']
            if item != "KRW" and item in target_item :
                count = acc_bal[0][i]['balance']
                unit_price = acc_bal[0][i]['avg_buy_price']
                input_money = float(count) * float(unit_price)

        qty = round(((input_money * 1.1) / ask_price), 8)
        
        ret = upbit.buy_limit_order(target_item, ask_price, qty)
        # print("[add water] item : ", target_item, "/ price : ", ask_price, "/ qty : ", qty)
        # print(ret)
    except :
        pass

def add_water_1_item(target_item) :
    try :
        print("add water 1 item : ", target_item)

        orderbook = pyupbit.get_orderbook(target_item)
        bids_asks = orderbook[0]['orderbook_units']
        price_sell = bids_asks[0]['ask_price']
        price_buy = bids_asks[0]['bid_price']

        acc_bal = upbit.get_balances()

        for i in range(0, len(acc_bal[0]), 1) :
            item = acc_bal[0][i]['currency']
            if item != "KRW" and item in target_item :
                count = float(acc_bal[0][i]['balance'])
                unit_price = float(acc_bal[0][i]['avg_buy_price'])

        A = count * unit_price              # 총 매입금액
        B = count * price_buy               # 총 평가금액
        T = 0
        FB = 0.0005
        FS = 0.0005
        # P = -0.01
        P = ADD_WATER_PER

        X = 1 + P + FB
        Y = 1 - T - FS

        qty = round(((Y*B - X*A) / (price_sell*X - price_buy*Y)), 8)
        price = price_sell
        
        ret = upbit.buy_limit_order(target_item, price, qty)
        # print("[add water] item : ", target_item, "/ price : ", price, "/ qty : ", qty)
        # # print(ret)
        
        
    except :
        pass

def get_now() :
    year = strftime("%Y", localtime())
    month = strftime("%m", localtime())
    day = strftime("%d", localtime())
    hour = strftime("%H", localtime())
    cmin = strftime("%M", localtime())
    sec = strftime("%S", localtime())

    now = "[" + year + "/" + month +"/" + day + " " + hour + ":" + cmin + ":" + sec + "] "

    return now