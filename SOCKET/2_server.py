from socket import *
# import socket
import pandas as pd
import time

HOST = ''
PORT = 5126

BUFSIZE = 1024
ADDR = (HOST, PORT)

df_acc = pd.DataFrame(columns = ['condition', 'cnt'])

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

# # 다음 client 소환
# HOST_NEXT = '165.132.105.40'  
# PORT_NEXT = 10036

# client_next = socket(AF_INET, SOCK_STREAM)
# client_next.connect((HOST_NEXT, PORT_NEXT))
# print("connected")

# print('--client information--')
# print(clientSocket)
receive = []
# 클라이언트로부터 메시지를 가져옴
while True :
    data = clientSocket.recv(65535)
    data = data.decode()        ## bytes -> string
    if data != "" :
        # print(data)
        data = data.split('\n')
        data.remove('')
        print(data)

        temp_str = data[0]
        updated = 0

        for m in range(len(df_acc)) :
            if temp_str == df_acc.condition[m] :
                temp_count = df_acc.cnt[m]
                new_count = temp_count + 1
                df_acc.cnt[m] = new_count
                updated = 1

        if updated == 0 :
            df_acc.loc[len(df_acc)] = [temp_str, 1]

        print("")
        print("누적")
        print(df_acc)
        print("")
        receive = []

    # try :
    #     temp = temp_str + '\n'
    #     client_next.sendall(temp.encode())
        
    # except :
    #     client_next.close()

