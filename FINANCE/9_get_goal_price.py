import pandas as pd 
import requests
import threading
import time
from bs4 import BeautifulSoup

ROE_LOW_LIMIT = 10
idx = 0

code_df = pd.read_html('http://kind.krx.co.kr/corpgeneral/corpList.do?method=download&searchType=13', header=0)[0] 
code_df.종목코드 = code_df.종목코드.map('{:06d}'.format) 
code_df = code_df[['회사명', '종목코드']]
code_df = code_df.rename(columns={'회사명': 'name', '종목코드': 'code'}) 

df2 = pd.DataFrame(columns = ['code', 'Q-5', 'Q-4', 'Q-3', 'Q-2', 'Q-1'])

# codecount = len(code_df)
codecount = 1

for i in range(0, codecount):
    try:
        if i%10 == 0:
            complete_ratio = round(i/codecount * 100, 1)
            print()
            print(str(i) + "/" + str(codecount) + "(" + str(complete_ratio) + "%) is completed")
            print()
        
        code = code_df['code'][i]

        # url = "https://finance.naver.com/item/main.nhn?code={code}".format(code=code)
        url = 'https://finance.naver.com/item/main.nhn?code=005930'
        # res = requests.get(url)
        res = requests.get(url).text
        # soup = BeautifulSoup(res.content, 'lxml')
        soup = BeautifulSoup(res, 'html.parser')

        print("Hello")
        # print(soup)
        # soup = BeautifulSoup(res.content, 'html.parser')

        # print(soup)
        # price = soup.select('#tbl-aveInfo > tbody > tr > td.col2.num')[0].text
        # price = soup.select('#tab_con1 > div:nth-child(4) > table > tbody > tr:nth-child(1) > td > em')[0].text
        # price = soup.select('#tab_con1 > div:nth-of-type(3) > table > tbody > tr > td > em')[0].text
        price = soup.select("#tab_con1 > div:nth-child(4) > table > tbody > tr:nth-child(1) > td > em").text
        # price = soup.select('#tbl-aveInfo > tbody > tr > td.col2.num')[0]
        # <td class="col2 num">64,500</td>
        print(price)
        # //*[@id="tab_con1"]/div[3]/table/tbody/tr[1]/td/em

        # if q1>ROE_LOW_LIMIT and q2>ROE_LOW_LIMIT and q3>ROE_LOW_LIMIT and q4>ROE_LOW_LIMIT and q5>ROE_LOW_LIMIT:
        #     idx = len(df2) + 1
        #     df2.loc[idx] = [code, q5, q4, q3, q2, q1]

    except:
        pass

# print(df2)