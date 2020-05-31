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
cnt_code = 1
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

        # url = "https://finance.naver.com/item/main.nhn?code={code}".format(code=code)

        url ="https://finance.daum.net/quotes/A{code}#home".format(code=code)

        res = requests.get(url)
        soup = BeautifulSoup(res.content, 'lxml')
        # result = soup.find('#boxDashboard > div > div > span.txtB > dl > dd:nth-child(8) > p')
        # result = soup.select('#boxDashboard > div > div > span.txtB > dl > dd:nth-child(8) > p')[0].text
        result = soup.select('#boxDashboard > div > div > span.txtB > dl > dd:nth-child(8) > p').text
        print(result)
        idx = len(df2) + 1
        df2.loc[idx] = [code, market_sum]
    except:
        pass

print(df2)