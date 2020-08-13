from socket import *
import pandas as pd
import pickle

HOST = ''
PORT = 5130

BUFSIZE = 1024
ADDR = (HOST, PORT)

serverSocket = socket(AF_INET, SOCK_STREAM)
serverSocket.bind(ADDR)
serverSocket.listen(100)
print('listen : ', PORT)
clientSocket, addr_info = serverSocket.accept()
print('connected')



while True :
    data = clientSocket.recv(65535)
    # data = pickle.loads(data)
    # data = data.decode()        ## bytes -> string
    if data != "" :
        data = pickle.loads(data)
        print(type(data))
        print(data)
        # data = data.split('\n')
        # row = data[0].split('\t')
        # print("data : ", row)