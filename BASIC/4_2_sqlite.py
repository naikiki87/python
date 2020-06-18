import sqlite3
import pandas as pd


conn = sqlite3.connect("test.db")

with conn:
    cur = conn.cursor()
    cur.execute("select * from dftest")
    rows = cur.fetchall()

    for row in rows:
        print(row)