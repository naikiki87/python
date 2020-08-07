# import pandas as pd

# temp_df = pd.DataFrame(columns = ['item1', 'item2'])

# # # print(temp_df)

# temp_df.loc[len(temp_df)] = [1, 2]
# print(temp_df)

# item_cnt = 2
# item1 = 1
# item2 = 3

# print("temp : ", temp_df.iloc[0, 1])

# for k in range(len(temp_df)) :
#     for a in range(1, item_cnt+1) :
#         if globals() ['item{}'.format(a)] == temp_df.iloc[k, a-1] :
#             update = 1
#         else :
#             update = 0

# print("update : ", update)

def forloop(item_cnt, start, for_cnt, receive) :
    if for_cnt == item_cnt :
        for i in range(start, len(receive)) :
            globals()['item{}'.format(for_cnt)] = receive[i]
            print("item",for_cnt,':', globals()['item{}'.format(for_cnt)])

    else :
        for i in range(start, len(receive)) :
            globals()['item{}'.format(for_cnt)] = receive[i]
            print("item",for_cnt,':', globals()['item{}'.format(for_cnt)])
            start = i + 1
            forloop(item_cnt, start, for_cnt+1, receive)

len_receive = 4
receive = [1]
forloop(len(receive), 0, 1, receive)
    

# for i1 in range(len(receive)) :
#         item1 = receive[i1][2]
#         for i2 in range(i1+1, len(receive)) :
#             item2 = receive[i2][2]
#             for i3 in range(i2+1, len(receive)) :
#                 AAAAAA