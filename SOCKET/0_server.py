from socket import *
import pandas as pd

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
# print('--client information--')
# print(clientSocket)
seq = 1
receive = []
# 클라이언트로부터 메시지를 가져옴
while True :
    data = clientSocket.recv(65535)
    data = data.decode()        ## bytes -> string
    if data != "" :
        data = data.split('\n')
        if seq == 1 :
            for i in range(len(data)) :
                receive.append(data[i])
            seq = 2
        elif seq == 2 :
            seq = 1
            for i in range(len(data)) :
                receive.append(data[i])

            receive.remove("")
            receive.remove("")

            print("[RECEIVE DATA]")

            for j in range(len(receive)) :
                updated = 0
                item = receive[j].split('\t')

                item_length = len(item)
                temp_str = ""
                for k in range(item_length-1) :     ## data transactionalizer
                    temp_str = temp_str + str(item[k])
                count = int(item[item_length-1])
                print(j, ' : ', temp_str, ' / ', count)

                for m in range(len(df_acc)) :
                    if temp_str == df_acc.condition[m] :
                        temp_count = df_acc.cnt[m]
                        new_count = temp_count + count
                        df_acc.cnt[m] = new_count
                        updated = 1

                if updated == 0 :
                    df_acc.loc[len(df_acc)] = [temp_str, count]

            print("")
            print("누적")
            print(df_acc)
            print("")
            receive = []

# # 소켓 종료 
# clientSocket.close()
# serverSocket.close()
# print('close')