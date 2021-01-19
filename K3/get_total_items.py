import FinanceDataReader as fdr
from datetime import datetime, timedelta, date
import pandas as pd
import sys
import time

pd.set_option('display.max_row', 20000)

today = date.today()
start_day = today + timedelta(days=-14)

df_krx = fdr.StockListing('KOSPI')

# print(df_krx)
# items = df_krx[['Symbol', 'Market', 'Name', 'Sector']]
# items2 = pd.DataFrame(columns=['code', 'market', 'name', 'sector'])
# items3 = pd.DataFrame(columns=['code', 'market', 'name', 'sector'])
# # print(items)

# print(len(items))



# for i in range(len(items)) :
#     market = items.Market[i]
#     sector = items.Sector[i]

#     if "KOSDAQ" in market or "KOSPI" in market :
#         items2.loc[len(items2)] = [items.Symbol[i], market, items.Name[i], sector]

# print(len(items2))

# for i in range(len(items2)) :
#     sector = str(items2.sector[i]).strip()

#     if "nan" not in sector :
#         items3.loc[len(items3)] = [items2.code[i], items2.market[i], items2.name[i], sector]

# print("final : ", len(items3))
# items3.to_csv('items.csv')

# final_item = []

# for i in range(len(items3)) :
#     final_item.append(items3.code[i])


# f_hook = open("total_items.py",'w')
# # date = "# DATE = " + self.get_now() + '\n'
# # f_hook.write(date)
# data = "ITEMS = " + str(final_item)
# f_hook.write(data)
# f_hook.close()


# f = open("items.txt", 'w', encoding='utf8')
# sys.stdout = f
# print(items3)
# sys.stdout = sys.__stdout__
# f.close()