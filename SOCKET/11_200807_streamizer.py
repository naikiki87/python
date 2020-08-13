from socket import *
import pandas as pd
import pickle
import time

# testdf = pd.DataFrame(columns = ['1', '2'])
# testdf.loc[0] = [1, 2]
# testdf.loc[1] = [2, 3]
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

client_next = socket(AF_INET, SOCK_STREAM)
client_next.connect((HOST_NEXT, PORT_NEXT))

send = []

# while True :
#     print(testdf)
#     send = pickle.dumps(testdf)

#     client_next.sendall(send)

#     time.sleep(1)


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
            # print("send : ", str_send)
            # row = "1234"
            # send_data = pickle.dumps(row)
            # client_next.sendall(send_data)
            # client_next.send(row)
            client_next.sendall(str_send.encode())
        
        except :
            client_next.close()

        send = []