import sys
import sqlite3
import time
import math
import pandas as pd
import pyupbit

import datetime
import config

TICKERS_1 = config.TICKERS_1
TICKERS_2 = config.TICKERS_2
TICKERS_3 = config.TICKERS_3

def func_SET_db_table() :
    conn = sqlite3.connect("item_status.db")
    cur = conn.cursor()
    sql = "create table if not exists STATUS (item text primary_key, step integer)"
    cur.execute(sql)
    conn.commit()

    # sql = "INSERT OR IGNORE INTO STATUS(item, step) VALUES(:ITEM, :STEP)"
    sql = "insert into STATUS(item, step) select :ITEM, :STEP where not exists (select * from STATUS where item=:ITEM)"
    for i in range(len(TICKERS_1)) :
        item = TICKERS_1[i]
        step = 0
        print("item : ", item, "step : ", step)
        cur.execute(sql, {"ITEM" : item, "STEP" : step})

    for i in range(len(TICKERS_2)) :
        item = TICKERS_2[i]
        step = 0
        print("item : ", item, "step : ", step)
        cur.execute(sql, {"ITEM" : item, "STEP" : step})

    for i in range(len(TICKERS_3)) :
        item = TICKERS_3[i]
        step = 0
        print("item : ", item, "step : ", step)
        cur.execute(sql, {"ITEM" : item, "STEP" : step})

    conn.commit()
    conn.close()

def func_GET_db_item(item):
    conn = sqlite3.connect("item_status.db")
    cur = conn.cursor()
    sql = "select step from STATUS where item = :ITEM"
    cur.execute(sql, {"ITEM" : item})
    row = cur.fetchone()
    conn.close()
    print("item : ", item, "step : ", int(row[0]))
    return int(row[0])

def func_INSERT_db_item(item, step):
    conn = sqlite3.connect("item_status.db")
    cur = conn.cursor()
    sql = "insert into STATUS (item, step) values(:ITEM, :STEP)"
    cur.execute(sql, {"ITEM" : item, "STEP" : step})
    conn.commit()
    conn.close()
    print("[MAIN] [func_INSERT_db_item] : INSERTED ", item)
def func_DELETE_db_item(code):
    conn = sqlite3.connect("item_status.db")
    cur = conn.cursor()
    sql = "delete from STATUS where code = :CODE"
    cur.execute(sql, {"CODE" : code})
    conn.commit()
    conn.close()

def update_db_step(item, step) :
    conn = sqlite3.connect("item_status.db")
    cur = conn.cursor()
    sql = "update STATUS set step=:STEP where item=:ITEM"
    cur.execute(sql, {"ITEM" : item, "STEP" : step})
    conn.commit()
    conn.close()

    return cur.rowcount

# func_SET_db_table()
# func_GET_db_item("KRW-XRP")
a = update_db_step("KRW-XRP", 0)
print(a)