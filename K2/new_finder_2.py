import FinanceDataReader as fdr
from datetime import datetime, timedelta, date
import pandas as pd
import sys
import total_items

pd.set_option('display.max_row', 20000)

today = date.today()
start_day = today + timedelta(days=-1)
day_bf_12 = today + timedelta(days=-12)
day_bf_100 = today + timedelta(days=-100)

print(day_bf_100)

item_list = total_items.ITEMS
print(len(item_list))

df_ratio = pd.DataFrame(columns=['code', 'ratio', 'duration'])

def find_item(duration) :
    print("duration : ", duration)
    today = date.today()
    time_d = int(-1 * duration)
    start_day = today + timedelta(days=time_d)

    for i in range(len(item_list)) :
    # for i in range(1) :
        if i % 200 == 0 :
            print(i, '/', len(item_list))

        code = item_list[i]

        df = fdr.DataReader(code, start_day, today)
        df = df.rename(columns={'Close':'end', 'Open':'start', 'High':'high', 'Low':'low', 'Volume' : 'vol'})
        df = df.sort_values(by=['Date'], axis=0, ascending=[False])  # sorting by std(descending)

        end0 = int(df.end.iloc[0])
        end1 = int(df.end.iloc[len(df) - 1])

        ratio = round((((end0 - end1) / end1) * 100), 2)

        if ratio < -15 :
            df_ratio.loc[len(df_ratio)] = [code, ratio, duration]

    print(df_ratio)

    if len(df_ratio) < 50 :
        duration = duration + 1
        find_item(duration)

find_item(10)