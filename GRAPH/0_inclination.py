print("inclination")

from socket import *
import pandas as pd
import sys
import time

file = open('test.txt', 'r')
s = file.read()
row = s.split('\n')

i = 0

pre_t = 0
pre_v = 0
pre_angle = 0

for i in range(len(row)) :
    data = row[i].split('\t')
    if i == 0 :
        pre_t = int(data[0])
        pre_v = int(data[1])
        continue
    else :
        dt = int(data[0]) - pre_t
        dv = int(data[1]) - pre_v

        angle = dv/dt
        print(data[0], ' : ', angle)

        if angle > pre_angle :
            print("up")
        pre_angle = angle

        pre_t = int(data[0])
        pre_v = int(data[1])

# while True :
#     if i == len(data) :
#         i = 0
#     row = data[i].split('\t')

#     try :
#         print("send : ", row)
#     except :
#         temp = 1