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

seq = 1
receive = []
tid = 0
# 클라이언트로부터 메시지를 가져옴
while True :
    data = clientSocket.recv(65535)
    data = data.decode()        ## bytes -> string
    if data != "" :
        tid = tid + 1
        data = data.split('\n')
        data.remove('')
        items = data[0].split('\t')
        # print("[RECEIVE DATA]")
        print(tid, ' : ', items)

        for i in range(len(items)) :
            updated = 0
            item = items[i]

            for j in range(len(df_acc)) :
                if item == df_acc.item[j] :
                    temp_count = df_acc.cnt[j]
                    new_count = temp_count + 1
                    df_acc.cnt[j] = new_count
                    updated = 1
            
            if updated == 0 :
                df_acc.loc[len(df_acc)] = [item, 1]

        for i in range(len(items)) :
            anchor = items[i]
            # print("anchor : ", anchor)
            j = i + 1
            for j in range(i+1, len(items)) :
                item2_part = items[j]
                item2 = str(anchor) + str(item2_part)
                # print(item2)

                updated_2 = 0

                for k in range(len(df_acc_2)) :
                    if item2 == df_acc_2.item[k] :
                        temp_count = df_acc_2.cnt[k]
                        new_count = temp_count + 1
                        df_acc_2.cnt[k] = new_count
                        updated_2 = 1
                
                if updated_2 == 0 :
                    df_acc_2.loc[len(df_acc_2)] = [item2, 1]

        print("")
        print("누적")
        print(df_acc)
        print(df_acc_2)
        print("")

        receive = []

# # 소켓 종료 
# clientSocket.close()
# serverSocket.close()
# print('close')