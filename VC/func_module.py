import pyupbit
import config

NEW_BUY_AMT = config.NEW_BUY_AMT

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
        print("[add water] item : ", target_item, "/ price : ", ask_price, "/ qty : ", qty)
        # print(ret)
    except :
        pass