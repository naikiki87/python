from socket import *
import pandas as pd
import sys

HOST = ''
PORT = 5128

BUFSIZE = 1024
ADDR = (HOST, PORT)

# 소켓 생성
serverSocket = socket(AF_INET, SOCK_STREAM)
# 소켓 주소 정보 할당 
serverSocket.bind(ADDR)
print('bind')
# 연결 수신 대기 상태
serverSocket.listen(100)
print('listen : ', PORT)
# 연결 수락
clientSocket, addr_info = serverSocket.accept()
print('connected')

HOST_NEXT = '165.132.105.36'  
PORT_NEXT = 5129
# # HOST_NEXT = sys.argv[1]
# # PORT_NEXT = sys.argv[2]

client_next = socket(AF_INET, SOCK_STREAM)
client_next.connect((HOST_NEXT, PORT_NEXT))

seq = 1
receive = []
send = []
tid = 0
# 클라이언트로부터 메시지를 가져옴
while True :
    data = clientSocket.recv(65535)
    data = data.decode()        ## bytes -> string
    if data != "" :
        data = data.split('\n')
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

        try :
            print("send : ", str_send)
            client_next.sendall(str_send.encode())
        
        except :
            client_next.close()

        # print("streamizer : ", send)
        # print("streamizer str : ", str_send)
            
        send = []