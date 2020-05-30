import pandas as pd 
import requests
import threading
import time
from bs4 import BeautifulSoup

code_df = pd.read_html('http://kind.krx.co.kr/corpgeneral/corpList.do?method=download&searchType=13', header=0)[0] 
code_df.종목코드 = code_df.종목코드.map('{:06d}'.format) 
code_df = code_df[['회사명', '종목코드']]
code_df = code_df.rename(columns={'회사명': 'name', '종목코드': 'code'}) 

idx = 0
cnt_code = 50
df2 = pd.DataFrame(columns = ['code', 'sum'])

for i in range(0, cnt_code):
    print(i)
    try:
        if i % 10 == 0:
            complete_ratio = round(i/cnt_code * 100, 1)
            print()
            print(str(i) + "/" + str(cnt_code) + "(" + str(complete_ratio) + "%) is completed")
            print()
        
        code = code_df['code'][i]
        get_last_3 = 1

        cnt_0_digit = 0

        url = url = "https://finance.naver.com/item/main.nhn?code={code}".format(code=code)
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
        idx = len(df2) + 1
        df2.loc[idx] = [code, market_sum]
    except:
        pass

print(df2)