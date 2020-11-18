from socket import *
import pandas as pd
import pickle
import sys
import time

INTERVAL = 1
DURATION = 10

file = open('trend.txt', 'r')
s = file.read()
row = s.split('\n')

i = 0
first = 1

prev = None
count = 0
step = 0
prev_step = None

while True :
    data = row[i].split('\t')
    try :
        if first == 1 :
            prev = float(data[0])
            first = 0
        else :
            cur = float(data[0])
            gap = cur - prev
            prev = cur

            if gap > 0 :
                step = step + 1
                count = 0
            elif gap < 0 :
                step = step - 1
                count = 0
            elif gap == 0 :
                count = count + 1
                if count >= DURATION :
                    print("END : ", step)
                    break

            print("cur : ", cur, "/ gap : ", gap, "/ step : ", step, "/ count : ", count)

    except :
        temp = 1

    time.sleep(INTERVAL)
    i = i + 1