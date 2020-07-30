from socket import *
import pandas as pd

HOST = ''
PORT = 5126

BUFSIZE = 1024
ADDR = (HOST, PORT)

df_acc = pd.DataFrame(columns = ['item', 'cnt'])
df_acc_2 = pd.DataFrame(columns = ['item', 'cnt'])

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

# HOST_NEXT = '165.132.105.40'  
# PORT_NEXT = 10048

# client_next = socket(AF_INET, SOCK_STREAM)
# client_next.connect((HOST_NEXT, PORT_NEXT))

seq = 1
receive = []
tid = 0
# 클라이언트로부터 메시지를 가져옴
while True :
    data = clientSocket.recv(65535)
    data = data.decode()        ## bytes -> string
    if data != "" :
        data = data.split('\n')
        if seq == 1 :
            for i in range(len(data)) :
                receive.append(data[i])
            receive.remove('')
            seq = 2
        elif seq == 2 :
            seq = 1
            for i in range(len(data)) :
                receive.append(data[i])
            receive.remove('')

        for i in range(len(receive)) :
            row = receive[i].split('\t')
            if int(row[3]) > int(row[1]) :
                print(row)

            # row = list(map(str, row))
            # str_row = '\t'.join(row)

            # try :
            #     str_row = str_row + '\n'
            #     print("send : ", str_row)
            #     client_next.sendall(str_row.encode())
            
            # except :
            #     client_next.close()

        receive = []

# # 소켓 종료 
# clientSocket.close()
# serverSocket.close()
# print('close')