from socket import *
import pandas as pd
import sys

agg_type = int(sys.argv[1])      ## 1 : tuple / 2 : time
agg_unit = int(sys.argv[2])

print("agg type : ", agg_type)
print("agg unit : ", agg_unit)

HOST = ''
PORT = 5128

BUFSIZE = 1024
ADDR = (HOST, PORT)

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
tuple_cnt = 0
time_cnt = 0
flag_create_df = 0
# 클라이언트로부터 메시지를 가져옴

def create_df(item_cnt) :
    for i in range(1, item_cnt+1) :
        cols = []
        for j in range(1, i+1) :
            item = "item" + str(j)
            cols.append(item)

        cols.append("cnt")
        cols.append("total")
        cols.append("support")

        globals()['item_{}_fp'.format(i)] = pd.DataFrame(columns = cols)

def item_1_FP(receive) :
    for i in range(len(receive)) :
        item = receive[i][2]
        update = 0

        for j in range(len(item_1_fp)) :
            if item == item_1_fp.item1[j] :
                temp_cnt = item_1_fp.cnt[j]
                new_cnt = temp_cnt + 1
                item_1_fp.cnt[j] = new_cnt
                update = 1
        if update == 0 :
            item_1_fp.loc[len(item_1_fp)] = [item, 1, '', '']
        
        total = 0

        for j in range(len(item_1_fp)) :
            total = total + item_1_fp.cnt[j]
        
        item_1_fp.total[0] = total

        for j in range(len(item_1_fp)) :
            support = item_1_fp.cnt[j] / total
            item_1_fp.support[j] = support
def item_2_FP(receive) :
    for i in range(len(receive)) :
        anchor = receive[i][2]
        for j in range(i+1, len(receive)) :
            update = 0
            item = receive[j][2]

            for k in range(len(item_2_fp)) :
                if anchor == item_2_fp.item1[k] :
                    if item == item_2_fp.item2[k] :
                        temp_cnt = item_2_fp.cnt[k]
                        new_cnt = temp_cnt + 1
                        item_2_fp.cnt[k] = new_cnt
                        update = 1
            
            if update == 0 :
                item_2_fp.loc[len(item_2_fp)] = [anchor, item, 1, '', '']

            total = 0

            for k in range(len(item_2_fp)) :
                total = total + item_2_fp.cnt[k]
            
            item_2_fp.total[0] = total

            for k in range(len(item_2_fp)) :
                support = item_2_fp.cnt[k] / total
                item_2_fp.support[k] = support
def item_3_FP(receive) :
    for i in range(len(receive)) :
        anchor_1 = receive[i][2]
        for j in range(i+1, len(receive)) :
            anchor_2 = receive[j][2]

            for k in range(j+1, len(receive)) :
                update = 0
                item = receive[k][2]

                for m in range(len(item_3_fp)) :
                    if anchor_1 == item_3_fp.item1[m] :
                        if anchor_2 == item_3_fp.item2[m] :
                            if item == item_3_fp.item3[m] :
                                temp_cnt = item_3_fp.cnt[m]
                                new_cnt = temp_cnt + 1
                                item_3_fp.cnt[m] = new_cnt
                                update = 1
                
                if update == 0 :
                    item_3_fp.loc[len(item_3_fp)] = [anchor_1, anchor_2, item, 1, '', '']

                total = 0

                for m in range(len(item_3_fp)) :
                    total = total + item_3_fp.cnt[m]
                
                item_3_fp.total[0] = total

                for m in range(len(item_3_fp)) :
                    support = item_3_fp.cnt[m] / total
                    item_3_fp.support[m] = support
def item_4_FP(receive) :
    for i in range(len(receive)) :
        anchor_1 = receive[i][2]
        for j in range(i+1, len(receive)) :
            anchor_2 = receive[j][2]
            for a in range(j+1, len(receive)) :
                anchor_3 = receive[a][2]
                for k in range(a+1, len(receive)) :
                    update = 0
                    item = receive[k][2]

                    for m in range(len(item_4_fp)) :
                        if anchor_1 == item_4_fp.item1[m] :
                            if anchor_2 == item_4_fp.item2[m] :
                                if anchor_3 == item_4_fp.item3[m] :
                                    if item == item_4_fp.item4[m] :
                                        temp_cnt = item_4_fp.cnt[m]
                                        new_cnt = temp_cnt + 1
                                        item_4_fp.cnt[m] = new_cnt
                                        update = 1
                    
                    if update == 0 :
                        item_4_fp.loc[len(item_4_fp)] = [anchor_1, anchor_2, anchor_3, item, 1, '', '']

                    total = 0

                    for m in range(len(item_4_fp)) :
                        total = total + item_4_fp.cnt[m]
                    
                    item_4_fp.total[0] = total

                    for m in range(len(item_4_fp)) :
                        support = item_4_fp.cnt[m] / total
                        item_4_fp.support[m] = support

while True :
    data = clientSocket.recv(65535)
    data = data.decode()        ## bytes -> string
    if data != "" :
        data = data.split('\n')
        row = data[0].split('\t')

        if first == 0 :
            if row[0] == index :
                receive.append(row)
            else :
                # print("receive : ", receive)
                tuple_cnt = tuple_cnt + 1
                print("tuple : ", tuple_cnt)
                item_cnt = len(receive)
                
                if flag_create_df == 0 :        ## df 동적 생성
                    create_df(item_cnt)
                    flag_create_df = 1

                item_1_FP(receive)
                item_2_FP(receive)
                item_3_FP(receive)
                item_4_FP(receive)

                if agg_type == 1 and tuple_cnt == agg_unit :
                    tuple_cnt = 0
                    print("---  1 item FP  ---")
                    print(item_1_fp)
                    print("---  2 item FP  ---")
                    print(item_2_fp)
                    print("---  3 item FP  ---")
                    print(item_3_fp)
                    print("---  4 item FP  ---")
                    print(item_4_fp)

                receive = []
                first = 1

        if first == 1 :
            index = row[0]
            first = 0
            receive.append(row)