from socket import *
import pandas as pd
import pickle
import sys

HOST = ''
PORT = int(sys.argv[2])
HOST_NEXT = sys.argv[3]
PORT_NEXT = int(sys.argv[4])

BUFSIZE = 1024
ADDR = (HOST, PORT)

serverSocket = socket(AF_INET, SOCK_STREAM)
serverSocket.bind(ADDR)
print('bind')
serverSocket.listen(100)
print('listen : ', PORT)
clientSocket, addr_info = serverSocket.accept()
print('connected')

client_next = socket(AF_INET, SOCK_STREAM)
client_next.connect((HOST_NEXT, PORT_NEXT))

receive = []
init_df = 0

def insert_new(item_cnt, items) :
    insert = []
    for i in range(item_cnt) :
        insert.append(items[i])
    insert.append(1)
    insert.append('')
    insert.append('')

    return insert
    
def looping(item_cnt, start, for_cnt, receive, temp_df, items) :
    if for_cnt == item_cnt :
        for i in range(start, len(receive)) :
            update = 0
            items.append(receive[i][2])
            
            for row in range(len(temp_df)) :
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
                temp_df.loc[len(temp_df)] = insert_new(item_cnt, items)      ## 신규 데이터를 insert

            items.pop()
        return temp_df

    else :
        for i in range(start, len(receive)) :
            items.append(receive[i][2])
            next_start = i + 1
            next_for_cnt = for_cnt + 1
            temp_df = looping(item_cnt, next_start, next_for_cnt, receive, temp_df, items)
            
            items.pop()

        return temp_df

def fp_finder(item_cnt, receive) :
    temp_df = globals()['item_{}_fp'.format(item_cnt)]
    items = []
    temp_df = looping(item_cnt, 0, 1, receive, temp_df, items)

    ## 공통부분 : count, support
    total = 0
    for x in range(len(temp_df)) :
        total = total + temp_df.cnt[x]
    temp_df.total[0] = total
    for x in range(len(temp_df)) :
        support = temp_df.cnt[x] / total
        temp_df.support[x] = support

    globals()['item_{}_fp'.format(item_cnt)] = temp_df

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
        data.remove('')

        for i in range(len(data)) :
            row = data[i].split('\t')
            receive.append(row)
        
        item_cnt = len(receive)
        print("receive : ", receive)
        ## receive complete

        if init_df == 0 :        ## item_cnt 만큼 df 동적 생성 - 1회 실행
            create_df(item_cnt)
            init_df = 1
        
        for i in range(1, item_cnt+1) :
            fp_finder(i, receive)
            print("")
            print(i, "FP")
            print(globals()['item_{}_fp'.format(i)])

        try :
            send_data = pickle.dumps(item_1_fp)     ## 1 항목 빈발
            client_next.sendall(send_data)
        except :
            print("error")

        receive = []