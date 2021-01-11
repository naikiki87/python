import FinanceDataReader as fdr
from datetime import datetime, timedelta, date
import pandas as pd
import sys
import total_items

pd.set_option('display.max_row', 20000)

today = date.today()
day_bf_14 = today + timedelta(days=-14)
day_bf_100 = today + timedelta(days=-100)
item_list = total_items.ITEMS

df_last = pd.DataFrame(columns = ['code', 'ratio_end_deg', 'mean_vol', 'today_vol', 'duration'])

df_last3 = pd.DataFrame(columns = ['code', 'ratio_end_deg', 'mean_vol', 'today_vol', 'duration'])

def run(duration) :
    check_price(duration)

def check_price(duration) :
    global df_last
    print("check price : ", duration)
    # for i in range(len(item_list)) :
    for i in range(400) :
        if i % 200 == 0 :
            print(i, '/', len(item_list))
        
        try :
            code = item_list[i]

            df = fdr.DataReader(code, day_bf_14, today)
            df = df.rename(columns={'Close':'end', 'Open':'start', 'High':'high', 'Low':'low', 'Volume' : 'vol'})
            df = df.sort_values(by=['Date'], axis=0, ascending=[False])  # sorting by std(descending)

            mean_vol = int(df.vol.mean())
            today_vol = int(df.vol.iloc[0])

            if mean_vol >= 50000 and today_vol >= 10000 :
                end6 = int(df.end.iloc[6])
                end5 = int(df.end.iloc[5])
                end4 = int(df.end.iloc[4])
                end3 = int(df.end.iloc[3])
                end2 = int(df.end.iloc[2])
                end1 = int(df.end.iloc[1])
                end0 = int(df.end.iloc[0])

                start6 = int(df.start.iloc[6])
                start5 = int(df.start.iloc[5])
                start4 = int(df.start.iloc[4])
                start3 = int(df.start.iloc[3])
                start2 = int(df.start.iloc[2])
                start1 = int(df.start.iloc[1])
                start0 = int(df.start.iloc[0])

                gap6 = end6 - start6
                gap5 = end5 - start5
                gap4 = end4 - start4
                gap3 = end3 - start3
                gap2 = end2 - start2
                gap1 = end1 - start1
                gap0 = end0 - start0

                if duration == 6 :
                    ratio_end = round((end0 / end6), 2)     ## 최근 감소율
                    ratio_end_deg = round(ratio_end, 1)
                    if ratio_end_deg <= 0.9 :
                        if end6 >= end5 and end5 >= end4 and end4 >= end3 and end3 >= end2 and end2 >= end1 and end1 >= end0 :
                            if gap3 < 0 and gap2 < 0 and gap1 < 0 and gap0 < 0 :
                                df_last.loc[len(df_last)] = [code, ratio_end_deg, mean_vol, today_vol, duration]

                elif duration == 5 :
                    ratio_end = round((end0 / end5), 2)     ## 최근 감소율
                    ratio_end_deg = round(ratio_end, 1)
                    if ratio_end_deg <= 0.9 :
                        if end5 >= end4 and end4 >= end3 and end3 >= end2 and end2 >= end1 and end1 >= end0 :
                            if gap3 < 0 and gap2 < 0 and gap1 < 0 and gap0 < 0 :
                                df_last.loc[len(df_last)] = [code, ratio_end_deg, mean_vol, today_vol, duration]

                elif duration == 4 :
                    ratio_end = round((end0 / end4), 2)     ## 최근 감소율
                    ratio_end_deg = round(ratio_end, 1)
                    if ratio_end_deg <= 0.9 :
                        if end4 >= end3 and end3 >= end2 and end2 >= end1 and end1 >= end0 :
                            if gap3 < 0 and gap2 < 0 and gap1 < 0 and gap0 < 0 :
                                df_last.loc[len(df_last)] = [code, ratio_end_deg, mean_vol, today_vol, duration]

                elif duration == 2 :
                    ratio_end = round((end0 / end2), 2)     ## 최근 감소율
                    ratio_end_deg = round(ratio_end, 1)
                    if ratio_end_deg <= 0.9 :
                        if end2 >= end1 and end1 >= end0 :
                            if gap2 < 0 and gap1 < 0 and gap0 < 0 :
                                df_last.loc[len(df_last)] = [code, ratio_end_deg, mean_vol, today_vol, duration]

        except :
            pass

    print("count df_last : ", len(df_last))

    if len(df_last) >= 100 :
        print("case 1")
        check_price2()

    else :
        if duration > 4 :
            print("case 2")
            duration = duration - 1
            check_price(duration)
        else :
            print("case 3")
            check_price2()

def check_price2() :
    global df_last
    df_last2 = pd.DataFrame(columns = ['code', 'ratio_end_deg', 'mean_vol', 'today_vol', 'duration', 'ratio'])
    df_last = df_last.sort_values(by=['duration', 'ratio_end_deg'], axis=0, ascending=[False, True])  # sorting by std(descending)
    df_last = df_last.reset_index(drop=True, inplace=False)     # re-indexing

    print("check price 2")
    print(df_last)

    for i in range(len(df_last)) :
        try :
            code = df_last.code[i]
            df = fdr.DataReader(code, day_bf_100, today)
            df = df.rename(columns={'Close':'end', 'Open':'start', 'High':'high', 'Low':'low', 'Volume' : 'vol'})
            df = df.sort_values(by=['Date'], axis=0, ascending=[False])  # sorting by std(descending)

            end0 = int(df.end.iloc[0])
            df_end = df[['end']]
            min_price = int(df_end.min())
            max_price = int(df_end.max())

            total_band = max_price - min_price
            p_pos = end0 - min_price
            ratio = round((p_pos / total_band), 2)

            # print("ratio : ", ratio, min_price, max_price, end0, total_band, p_pos)

            if ratio > 0.05 and ratio < 0.25 :
                
                ratio_end_deg = df_last.ratio_end_deg[i]
                mean_vol = df_last.mean_vol[i]
                today_vol = df_last.today_vol[i]
                duration = df_last.duration[i]
                print("in : ", ratio, duration)
                df_last2.loc[len(df_last2)] = [code, ratio_end_deg, mean_vol, today_vol, duration, ratio]
        except :
            pass
    
    print("final : ", df_last2)

run(4)