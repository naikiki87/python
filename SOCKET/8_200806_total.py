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


def check_item(item, item_cnt, temp_df) :
    update = 0

    if item_cnt == 1 :
        for k in range(len(temp_df)) :
            if item == temp_df.item1[k] :
                temp_cnt = temp_df.cnt[k]
                new_cnt = temp_cnt + 1
                temp_df.cnt[k] = new_cnt
                update = 1

def insert(item_cnt, item) :
    insert = []
    for i in range(1, item_cnt) :
        insert.append("item"+str(i))
    insert.append(item)
    insert.append(1)
    insert.append('')
    insert.append('')

    print("insert : ", insert)
    return insert

def insert2(item_cnt, items) :
    insert = []
    for i in range(item_cnt) :
        insert.append(items[i])
    insert.append(1)
    insert.append('')
    insert.append('')

    print("insert : ", insert)
    return insert

def forloop(item_cnt, start, for_cnt, receive, temp_df, items) :
    print("for loop start 2")
    if for_cnt == item_cnt :
        for i in range(start, len(receive)) :
            update = 0
            items.append(receive[i][2])
            # globals()['item{}'.format(item_cnt)] = receive[i][2]
            
            for row in range(len(temp_df)) :
                # for a in range(1, item_cnt+1) :
                #     if globals()['item{}'.format(a)] == temp_df.iloc[row, a-1] :
                #         update = 1
                #     else :
                #         update = 0
                #         break

                for a in range(item_cnt) :
                    if items[a] == temp_df.iloc[row, a] :
                        update = 1
                    else :
                        update = 0
                        break

                if update == 1 :        ## 동일한 item set 이 있는 경우
                    temp_cnt = temp_df.cnt[row]
                    new_cnt = temp_cnt + 1
                    temp_df.cnt[row] = new_cnt
                    break               ## temp_df를 더이상 체크하지 않고 빠져나감
            
            if update == 0 :
                # temp_df.loc[len(temp_df)] = insert(item_cnt, globals() ['item{}'.format(item_cnt)])      ## 신규 데이터를 insert
                # temp_df.loc[len(temp_df)] = insert(item_cnt, items[item_cnt-1])      ## 신규 데이터를 insert
                temp_df.loc[len(temp_df)] = insert2(item_cnt, items)      ## 신규 데이터를 insert

            items.pop()
        return temp_df

    else :
        print("for loop over 2")
        for i in range(start, len(receive)) :
            items.append(receive[i][2])
            # globals()['item{}'.format(for_cnt)] = receive[i][2]
            # print("item",for_cnt,':', globals()['item{}'.format(for_cnt)])
            next_start = i + 1
            next_for_cnt = for_cnt + 1
            temp_df = forloop(item_cnt, next_start, next_for_cnt, receive, temp_df, items)
            
            items.pop()

        return temp_df

# len_receive = 4
# receive = [1]
# forloop(len(receive), 0, 1, receive)
 
# def forloop(item_cnt, receive, temp_df) :
#     print("for loop start : ", item_cnt)
#     # if item_cnt == 1 :
#     for i in range(len(receive)) :
#         update = 0
#         globals()['item{}'.format(item_cnt)] = receive[i][2]
        
#         for row in range(len(temp_df)) :
#             for a in range(1, item_cnt+1) :
#                 if globals()['item{}'.format(a)] == temp_df.iloc[row, a-1] :
#                     update = 1
#                 else :
#                     update = 0
#                     break

#             if update == 1 :        ## 동일한 item set 이 있는 경우
#                 temp_cnt = temp_df.cnt[row]
#                 new_cnt = temp_cnt + 1
#                 temp_df.cnt[row] = new_cnt
#                 break               ## temp_df를 더이상 체크하지 않고 빠져나감
        
#         if update == 0 :
#             temp_df.loc[len(temp_df)] = insert(item_cnt, globals() ['item{}'.format(item_cnt)])      ## 신규 데이터를 insert

#     return temp_df

def item_test(item_cnt, receive) :
    print("item test start")
    temp_df = globals()['item_{}_fp'.format(item_cnt)]
    print("item test temp_df : ", temp_df)

    # temp_df = forloop(item_cnt, receive, temp_df)
    items = []
    temp_df = forloop(item_cnt, 0, 1, receive, temp_df, items)

    ## 공통부분 : count, support
    total = 0
    for x in range(len(temp_df)) :
        total = total + temp_df.cnt[x]
    temp_df.total[0] = total
    for x in range(len(temp_df)) :
        support = temp_df.cnt[x] / total
        temp_df.support[x] = support

    globals()['item_{}_fp'.format(item_cnt)] = temp_df

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
        anchor_1 = receive[i][2]
        for j in range(i+1, len(receive)) :
            update = 0
            item = receive[j][2]

            for k in range(len(item_2_fp)) :
                if anchor_1 == item_2_fp.item1[k] :
                    if item == item_2_fp.item2[k] :
                        temp_cnt = item_2_fp.cnt[k]
                        new_cnt = temp_cnt + 1
                        item_2_fp.cnt[k] = new_cnt
                        update = 1
            
            if update == 0 :
                item_2_fp.loc[len(item_2_fp)] = [anchor_1, item, 1, '', '']

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
                tuple_cnt = tuple_cnt + 1
                print("tuple : ", tuple_cnt)
                item_cnt = len(receive)
                
                if flag_create_df == 0 :        ## df 동적 생성 - 1회
                    create_df(item_cnt)
                    flag_create_df = 1

                for i in range(1, item_cnt+1) :
                    item_test(i, receive)


                # if agg_type == 1 and tuple_cnt == agg_unit :
                #     tuple_cnt = 0
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