import FinanceDataReader as fdr
from datetime import datetime, timedelta, date
import pandas as pd
import sys
import time

# pd.set_option('display.max_row', 20000)

file = open('item_3.txt', 'r')
s = file.read()
row = s.split('\n')

final_item = []

for i in range(len(row)) :
    if len(row[i]) == 6 :
        final_item.append(row[i])

f_hook = open("total_items.py",'w')
data = "ITEMS = " + str(final_item)
f_hook.write(data)
f_hook.close()
    



# items3 = pd.read_csv('item_3.txt', encoding='euc-kr')
# print(items3)




