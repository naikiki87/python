from socket import *
import pandas as pd
import pickle
import sys
import time

HOST_NEXT = sys.argv[1]
PORT_NEXT = int(sys.argv[2])
INTERVAL = int(sys.argv[3])

next_client = socket(AF_INET, SOCK_STREAM)
next_client.connect((HOST_NEXT, PORT_NEXT))

file = open('2d_int_int.txt', 'r')
s = file.read()
data = s.split('\n')

i = 0

while True :
    if i == len(data) :
        i = 0
    row = data[i].split('\t')

    try :
        print("send : ", row)
        send_data = pickle.dumps(row)
        next_client.sendall(send_data)
    except :
        next_client.close()

    time.sleep(INTERVAL)
    i = i + 1