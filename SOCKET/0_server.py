from socket import *
import pandas as pd

HOST = ''
PORT = 5126

BUFSIZE = 1024
ADDR = (HOST, PORT)

df_acc = pd.DataFrame(columns = ['a', 'b', 'c', 'd', 'cnt'])

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
# print('--client information--')
# print(clientSocket)

# 클라이언트로부터 메시지를 가져옴
while True :
    data = clientSocket.recv(65535)
    data = data.decode()        ## bytes -> string
    data = data.split('\n')

    for i in range(len(data)-1) :
        item = data[i].split('\t')
        print(item)

# # 소켓 종료 
# clientSocket.close()
# serverSocket.close()
# print('close')