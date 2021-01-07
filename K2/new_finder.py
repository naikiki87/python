import FinanceDataReader as fdr
from datetime import datetime, timedelta, date
import pandas as pd
import sys
import total_items

pd.set_option('display.max_row', 20000)

today = date.today()
day_bf_12 = today + timedelta(days=-12)
day_bf_100 = today + timedelta(days=-100)

print(day_bf_100)

item_list = total_items.ITEMS
print(len(item_list))

# # for i in range(len(item_list)) :
for i in range(1) :
    code = item_list[i]
    print("code : ", code)

    df = fdr.DataReader(code, day_bf_12, today)
    df = df.sort_values(by=['Date'], axis=0, ascending=[False])  # sorting by std(descending)
    print(df)
    print("ke : ", len(df))

    end0 = int(df.Close.iloc[len(df)-1])
    end1 = int(df.Close.iloc[len(df)-2])
    end2 = int(df.Close.iloc[len(df)-3])
    end3 = int(df.Close.iloc[len(df)-4])
    end4 = int(df.Close.iloc[len(df)-5])
    end5 = int(df.Close.iloc[len(df)-6])

    start0 = int(df.Open.iloc[len(df)-1])
    start1 = int(df.Open.iloc[len(df)-2])
    start2 = int(df.Open.iloc[len(df)-3])
    start3 = int(df.Open.iloc[len(df)-4])
    start4 = int(df.Open.iloc[len(df)-5])
    start5 = int(df.Open.iloc[len(df)-6])

    print(end0, end1, end2, end3, end4, end5)
    print(start0, start1, start2, start3, start4, start5)

# print("item list Complete")
# # for i in range(len(df_item)) :
# for i in range(200) :
#     if i % 10 == 0 :
#         print(i)
    
#     code = df_item.Symbol[i]
#     # print("code : ", code)
    
#     df = fdr.DataReader(code, '2020-12-21', '2021-01-07')
#     # end = df.close
