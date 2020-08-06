from socket import *
import pandas as pd

HOST = ''
PORT = 5128

BUFSIZE = 1024
ADDR = (HOST, PORT)

# df_acc = pd.DataFrame(columns = ['item', 'cnt'])
item_1_fp = pd.DataFrame(columns = ['item1', 'cnt', 'total', 'support'])
item_2_fp = pd.DataFrame(columns = ['item1', 'item2', 'cnt', 'total', 'support'])
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

first = 1
seq = 1
receive = []
tid = 0
index = 0
# 클라이언트로부터 메시지를 가져옴

def item_1_FP(receive) :
    for i in range(len(receive)) :
        item = receive[i][2]
        update_1 = 0

        for j in range(len(item_1_fp)) :
            if item == item_1_fp.item1[j] :
                temp_cnt = item_1_fp.cnt[j]
                new_cnt = temp_cnt + 1
                item_1_fp.cnt[j] = new_cnt
                update_1 = 1
        if update_1 == 0 :
            item_1_fp.loc[len(item_1_fp)] = [item, 1, '', '']
        
        total_1 = 0

        for j in range(len(item_1_fp)) :
            total_1 = total_1 + item_1_fp.cnt[j]
        
        item_1_fp.total[0] = total_1

        for j in range(len(item_1_fp)) :
            support = item_1_fp.cnt[j] / total_1
            item_1_fp.support[j] = support

def item_2_FP(receive) :
    for i in range(len(receive)) :
        anchor = receive[i][2]
        for j in range(i+1, len(receive)) :
            update_2 = 0
            item2 = receive[j][2]

            for k in range(len(item_2_fp)) :
                if anchor == item_2_fp.item1[k] :
                    if item2 == item_2_fp.item2[k] :
                        temp_cnt = item_2_fp.cnt[k]
                        new_cnt = temp_cnt + 1
                        item_2_fp.cnt[k] = new_cnt
                        update_2 = 1
            
            if update_2 == 0 :
                item_2_fp.loc[len(item_2_fp)] = [anchor, item2, 1, '', '']

            total_2 = 0

            for j in range(len(item_2_fp)) :
                total_2 = total_2 + item_2_fp.cnt[j]
            
            item_2_fp.total[0] = total_2

            for j in range(len(item_2_fp)) :
                support = item_2_fp.cnt[j] / total_2
                item_2_fp.support[j] = support

while True :
    data = clientSocket.recv(65535)
    data = data.decode()        ## bytes -> string
    if data != "" :
        data = data.split('\n')
        data.remove('')
        row = data[0].split('\t')

        if first == 0 :
            if row[0] == index :
                receive.append(row)
            else :
                print("receive : ", receive)
                item_cnt = len(receive)
                print("total FP cnt : ", item_cnt)

                item_1_FP(receive)
                item_2_FP(receive)



                #### 1 item 빈발
                # for i in range(len(receive)) :
                #     item = receive[i][2]
                #     update_1 = 0

                #     for j in range(len(item_1_fp)) :
                #         if item == item_1_fp.item1[j] :
                #             temp_cnt = item_1_fp.cnt[j]
                #             new_cnt = temp_cnt + 1
                #             item_1_fp.cnt[j] = new_cnt
                #             update_1 = 1
                #     if update_1 == 0 :
                #         item_1_fp.loc[len(item_1_fp)] = [item, 1, '', '']
                    
                #     total_1 = 0

                #     for j in range(len(item_1_fp)) :
                #         total_1 = total_1 + item_1_fp.cnt[j]
                    
                #     item_1_fp.total[0] = total_1

                #     for j in range(len(item_1_fp)) :
                #         support = item_1_fp.cnt[j] / total_1
                #         item_1_fp.support[j] = support

                ### 2 item 빈발
                # for i in range(len(receive)) :
                #     anchor = receive[i][2]
                #     for j in range(i+1, len(receive)) :
                #         update_2 = 0
                #         item2 = receive[j][2]

                #         for k in range(len(item_2_fp)) :
                #             if anchor == item_2_fp.item1[k] :
                #                 if item2 == item_2_fp.item2[k] :
                #                     temp_cnt = item_2_fp.cnt[k]
                #                     new_cnt = temp_cnt + 1
                #                     item_2_fp.cnt[k] = new_cnt
                #                     update_2 = 1
                        
                #         if update_2 == 0 :
                #             item_2_fp.loc[len(item_2_fp)] = [anchor, item2, 1, '', '']

                #         total_2 = 0

                #         for j in range(len(item_2_fp)) :
                #             total_2 = total_2 + item_2_fp.cnt[j]
                        
                #         item_2_fp.total[0] = total_2

                #         for j in range(len(item_2_fp)) :
                #             support = item_2_fp.cnt[j] / total_2
                #             item_2_fp.support[j] = support

                print("---  1 item FP  ---")
                print(item_1_fp)
                print("---  2 item FP  ---")
                print(item_2_fp)
                receive = []
                first = 1

        if first == 1 :
            index = row[0]
            first = 0
            receive.append(row)