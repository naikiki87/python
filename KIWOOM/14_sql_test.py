import sys
import sqlite3
import time
from time import localtime, strftime
import pandas as pd

def get_status(code) :
    print("called", code)
    conn = sqlite3.connect("item_status.db")
    cur = conn.cursor()
    sql = "select status from STATUS where code = ?"
    cur.execute(sql, [code])

    row = cur.fetchone()
    conn.close()

    if row is None:
        return "none"
    else:
        return row[0]

# val = get_status("005935")
# print(val)

str1 = "abc"

if str1 in "abcde" :
    print("true")
    