from socket import *
import pandas as pd

HOST = ''
PORT = 5126

BUFSIZE = 1024
ADDR = (HOST, PORT)

df_acc = pd.DataFrame(columns = ['item', 'cnt'])
df_acc_2 = pd.DataFrame(columns = ['item1', 'item2', 'cnt', 'total', 'support'])

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
                # print("row : ", row)

                updated2 = 0

                for m in range(len(df_acc_2)) :
                    if row[1] == df_acc_2.item1[m] :
                        if row[3] == df_acc_2.item2[m] :
                            # df_acc_2.total[0] = df_acc_2.total[0] + 1     ## total 증가
                            temp_count = df_acc_2.cnt[m]
                            new_count = temp_count + 1
                            df_acc_2.cnt[m] = new_count
                            updated2 = 1

                if updated2 == 0 :
                    print("new insert")
                    df_acc_2.loc[len(df_acc_2)] = [row[1], row[3], 1, '', '']

                total = 0
                for n in range(len(df_acc_2)) :
                    total = total + df_acc_2.cnt[n]

                df_acc_2.total[0] = total

                for n in range(len(df_acc_2)) :
                    cnt = df_acc_2.cnt[n]
                    support = cnt / total
                    df_acc_2.support[n] = support

        print("누적")
        print(df_acc_2)

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