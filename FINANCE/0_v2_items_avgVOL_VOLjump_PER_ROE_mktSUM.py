import pandas as pd 
import requests
import threading
import time
from bs4 import BeautifulSoup

idx = 0
idx2 = 0
idx3 = 0
idx4 = 0
# VOL_YESTERDAY = 1000000
SHOW_SCALE = 5

VOL_FIN_PAGE = 3
VOL_AVERAGE = 100000    # 평균 volume filtering 하한치
VOL_RATIO_YESTERDAY = 1
VOL_RATIO_TODAY_LOW = 0.7
VOL_RATIO_TODAY_HI = 10

PER_LIMIT = 100

ROE_LOW_LIMIT = 0

SUM_LOW_LIMIT = 100     # 시가총액 하한치(단위 : 억원)

code_df = pd.read_html('http://kind.krx.co.kr/corpgeneral/corpList.do?method=download&searchType=13', header=0)[0] 
code_df.종목코드 = code_df.종목코드.map('{:06d}'.format) 
code_df = code_df[['회사명', '종목코드']]
code_df = code_df.rename(columns={'회사명': 'name', '종목코드': 'code'}) 

df2 = pd.DataFrame(columns = ['code', 'Vol(D)', 'Vol(D-1)', 'Vol(Avg)'])

# cnt_code = len(code_df)
cnt_code = 200

for i in range(0, cnt_code):
    try:
        if i % 25 == 0:
            complete_ratio = round(i/cnt_code * 100, 1)
            print()
            print(str(i) + "/" + str(cnt_code) + "(" + str(complete_ratio) + "%) is completed")
            print()
        
        code = code_df['code'][i]

        url = 'http://finance.naver.com/item/sise_day.nhn?code={code}'.format(code=code) 
        df = pd.read_html(url, header=0)[0]
        # df = df.dropna()

        for page in range(2, VOL_FIN_PAGE) :
            url = 'http://finance.naver.com/item/sise_day.nhn?code={code}&page={page}'.format(code=code, page=page) 
            df = df.append(pd.read_html(url, header=0)[0], ignore_index=True) 

        df = df.rename(columns={'날짜':'date', '종가':'end', '전일비':'gap', '시가':'start', '고가':'high', '저가':'low', '거래량' : 'vol'})
        df = df.dropna()

        # print(df)

        vol_average = int(round(df['vol'].mean(), 0))

        # print(vol_average)

        today_vol = df.iloc[0]['vol']
        day1before_vol = df.iloc[1]['vol']
        day2before_vol = df.iloc[2]['vol']
        
        today_start = df.iloc[0]['start']
        day1before_start = df.iloc[1]['start']
        day2before_start = df.iloc[2]['start']

        today_end = df.iloc[0]['end']
        day1before_end = df.iloc[1]['end']
        day2before_end = df.iloc[2]['end']

        today_posneg = today_end - today_start
        day1before_posneg = day1before_end - day1before_start
        day2before_posneg = day2before_end - day2before_start

        today_ratio = today_vol/day1before_vol
        day1before_ratio = day1before_vol/day2before_vol

        # if day1before_vol > VOL_YESTERDAY:
        if vol_average > VOL_AVERAGE :
            if day1before_ratio > VOL_RATIO_YESTERDAY:    # 어제 거래량이 그저께 거래량보다 급등한 경우
                if today_ratio > VOL_RATIO_TODAY_LOW and today_ratio < VOL_RATIO_TODAY_HI:   # 금일 거래량이 어제 거래량에 상당한 수준
                    if day1before_posneg > 0 :  # 어제 양봉일 경우
                        idx = len(df2) + 1
                        df2.loc[idx] = [code, today_ratio, day1before_ratio, vol_average]
    except:
        pass

print(df2)

cnt_after_vol = len(df2)
# next_scale = int(cnt_after_vol / 10)
print()
print("Volume Search Complete : " + str(cnt_after_vol) + " has filtered.")
print("Calculating PER value for " + str(cnt_after_vol) + " items.")
print()

df3 = pd.DataFrame(columns = ['code', 'PER', 'Vol(D)', 'Vol(D-1)', 'Vol(Avg)'])

for i in range(0, cnt_after_vol+1):
    try:
        if i % SHOW_SCALE == 0:
            complete_ratio = round(i/cnt_after_vol * 100, 1)
            print()
            print(str(i) + "/" + str(cnt_after_vol) + "(" + str(complete_ratio) + "%) is completed")
            print()
        
        code = df2['code'][i]

        url = "https://finance.naver.com/item/main.nhn?code={code}".format(code=code)
        res = requests.get(url)
        soup = BeautifulSoup(res.content, 'lxml')
        result = soup.find('em', id='_per')

        val_PER = float(result.text)

        if val_PER <= PER_LIMIT :
            idx2 = len(df3) + 1
            today_ratio = df2['Vol(D)'][i]
            day1before_ratio = df2['Vol(D-1)'][i]
            vol_average = df2['Vol(Avg)'][i]

            df3.loc[idx2] = [code, val_PER, today_ratio, day1before_ratio, vol_average]
    except:
        pass

print(df3)

cnt_after_PER = len(df3)
# next_scale = int(cnt_after_PER / 10)
print()
print("PER Search Complete : " + str(cnt_after_PER) + " has filtered.")
print("Calculating ROE value for " + str(cnt_after_PER) + " items.")
print()

df4 = pd.DataFrame(columns = ['code', 'PER', 'Vol(D)', 'Vol(D-1)', 'Vol(Avg)', 'ROE(Q-5)', 'ROE(Q-4)', 'ROE(Q-3)', 'ROE(Q-2)', 'ROE(Q-1)'])

for i in range(0, cnt_after_PER+1):
    try:
        if i % SHOW_SCALE == 0:
            complete_ratio = round(i/cnt_after_PER * 100, 1)
            print()
            print(str(i) + "/" + str(cnt_after_PER) + "(" + str(complete_ratio) + "%) is completed")
            print()
        
        code = df3['code'][i]

        # print(code)

        url = "https://finance.naver.com/item/main.nhn?code={code}".format(code=code)
        res = requests.get(url)
        soup = BeautifulSoup(res.content, 'lxml')
        q1 = float(soup.select('#content > div.section.cop_analysis > div.sub_section > table > tbody > tr:nth-child(6) > td:nth-child(10)')[0].text)
        q2 = float(soup.select('#content > div.section.cop_analysis > div.sub_section > table > tbody > tr:nth-child(6) > td:nth-child(9)')[0].text)
        q3 = float(soup.select('#content > div.section.cop_analysis > div.sub_section > table > tbody > tr:nth-child(6) > td:nth-child(8)')[0].text)
        q4 = float(soup.select('#content > div.section.cop_analysis > div.sub_section > table > tbody > tr:nth-child(6) > td:nth-child(7)')[0].text)
        q5 = float(soup.select('#content > div.section.cop_analysis > div.sub_section > table > tbody > tr:nth-child(6) > td:nth-child(6)')[0].text)

        diffq12 = q1 - q2
        diffq23 = q2 - q3
        diffq34 = q3 - q4
        diffq45 = q4 - q5

        # if diffq12 > 0 and diffq23 > 0 and diffq34 > 0 and diffq45 > 0 :

        if q1>ROE_LOW_LIMIT and q2>ROE_LOW_LIMIT and q3>ROE_LOW_LIMIT and q4>ROE_LOW_LIMIT and q5>ROE_LOW_LIMIT:
            idx3 = len(df4) + 1
            val_PER = df3['PER'][i]
            today_ratio = df3['Vol(D)'][i]
            day1before_ratio = df3['Vol(D-1)'][i]
            vol_average = df3['Vol(Avg)'][i]
            df4.loc[idx3] = [code, val_PER, today_ratio, day1before_ratio, vol_average, q5, q4, q3, q2, q1]
    except:
        pass

print()
print(df4)

cnt_after_ROE = len(df4)
print()
print("ROE Search Complete : " + str(cnt_after_ROE) + " has filtered.")
print("Calculating market_SUM value for " + str(cnt_after_ROE) + " items.")
print()

# df5 = pd.DataFrame(columns = ['code', 'PER', 'Vol(D)', 'Vol(D-1)', 'Vol(Avg)', 'ROE(Q-1)', 'mktSUM'])
df5 = pd.DataFrame(columns = ['code', 'mktSUM', 'PER', 'Vol(Avg)', 'ROE(Q-1)'])

for i in range(0, cnt_after_ROE + 1):
    # print(i)
    try:
        if i % SHOW_SCALE == 0:
            complete_ratio = round(i/cnt_after_ROE * 100, 1)
            print()
            print(str(i) + "/" + str(cnt_after_ROE) + "(" + str(complete_ratio) + "%) is completed")
            print()
        
        code = df4['code'][i]
        get_last_3 = 1

        cnt_0_digit = 0

        url = "https://finance.naver.com/item/main.nhn?code={code}".format(code=code)
        res = requests.get(url)
        soup = BeautifulSoup(res.content, 'lxml')
        result = soup.select('#_market_sum')[0].text.strip()
        result = result.replace(',', '')
        result = result.replace('\t', '')
        result = result.replace('\n', '')

        nextstr = []
        lensum = len(result)
        ptr = 0
        for k in range(0, lensum):
            if result[k] == '조':
                ptr = k
                break           
            nextstr.append(result[k])
        
        if ptr != 0 :
            cnt_0_digit = 4 - (lensum - (ptr + 1))

            for m in range(0, cnt_0_digit) :
                nextstr.append('0')
            
            for n in range(ptr+1, lensum) :
                nextstr.append(result[n])

        market_sum = int("".join(nextstr))

        if market_sum > SUM_LOW_LIMIT :
            idx4 = len(df5) + 1

            val_PER = df4['PER'][i]
            today_ratio = df4['Vol(D)'][i]
            day1before_ratio = df4['Vol(D-1)'][i]
            vol_average = df4['Vol(Avg)'][i]
            q1 = df4['ROE(Q-1)'][i]

            # df5.loc[idx4] = [code, val_PER, today_ratio, day1before_ratio, vol_average, q1, market_sum]
            df5.loc[idx4] = [code, market_sum, val_PER, vol_average, q1]
    except:
        pass

print()
print(df5)