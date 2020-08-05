from socket import *
import pandas as pd

HOST = ''
PORT = 5127

BUFSIZE = 1024
ADDR = (HOST, PORT)

# df_acc = pd.DataFrame(columns = ['item', 'cnt'])
df_acc = pd.DataFrame(columns = ['tid', 'iid1', 'item1', 'iid2', 'item2'])
df_acc_2 = pd.DataFrame(columns = ['iid1', 'item1', 'iid2', 'item2', 'cnt', 'total', 'support'])
df_acc_3 = pd.DataFrame(columns = ['item1', 'item2', 'item3', 'cnt', 'total', 'support'])

# 소켓 생성
serverSocket = socket(AF_INET, SOCK_STREAM)

# 소켓 주소 정보 할당 
serverSocket.bind(ADDR)
print('bind')

# 연결 수신 대기 상태python
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

            print("receive : ", receive)

            for i in range(len(receive)) :
                row = receive[i].split('\t')
                # row[3] = bs2.iid2
                # row[5] = bs1.iid1
                if row[3] == row[5] :
                    # print("row : ", row)

                    updated = 0

                    for m in range(len(df_acc_3)) :
                        if row[2] == df_acc_3.item1[m] :
                            if row[4] == df_acc_3.item2[m] :
                                if row[6] == df_acc_3.item3[m] :
                                    temp_count = df_acc_3.cnt[m]
                                    new_count = temp_count + 1
                                    df_acc_3.cnt[m] = new_count
                                    updated = 1
                        
                        if updated == 0 :
                            print("new item inserted")
                            df_acc_3.loc[len(df_acc_3)] = [row[2], row[4], row[6], 1, '', '']

                        total = 0

                        for n in range(len(df_acc_3)) :
                            total = total + df_acc_3.cnt[n]

                        df_acc_3.total[0] = total

                        for n in range(len(df_acc3)) :
                            support = df_acc_3.cnt[n] / total
                            df_acc_3.support[n] = support

            print("누적")
            print(df_acc_3)
            receive = []        ## receive initialize