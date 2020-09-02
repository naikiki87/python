from socket import *
import pandas as pd
import pickle
import time
import sys

HOST = ''
PORT = int(sys.argv[2])
HOST_NEXT = sys.argv[3]
PORT_NEXT = int(sys.argv[4])

BUFSIZE = 1024
ADDR = (HOST, PORT)

serverSocket = socket(AF_INET, SOCK_STREAM)
serverSocket.bind(ADDR)
print('bind')
serverSocket.listen(100)
print('listen : ', PORT)
clientSocket, addr_info = serverSocket.accept()
print('connected')

# client_next = socket(AF_INET, SOCK_STREAM)
# client_next.connect((HOST_NEXT, PORT_NEXT))

send = []

while True :
    data = clientSocket.recv(65535)
    data = data.decode()        ## bytes -> string
    if data != "" :
        data = data.split('\r\n')
        print("data1 : ", data)
        row = data[0].split('\t')
        print("data : ", row)

        str_send = ""
        for i in range(1, len(row)) :
            temp = []
            temp.append(row[0])     ## tid
            temp.append(i)          ## iid
            temp.append(row[i])     ## item
            send.append(temp)

            str_send = str_send + str(row[0]) + '\t' + str(i) + '\t' + str(row[i]) + '\n'

        # try :
        #     client_next.sendall(str_send.encode())
        
        # except :
        #     client_next.close()

        send = []