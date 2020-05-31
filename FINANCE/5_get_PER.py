import pandas as pd 
import requests
import threading
import time
from bs4 import BeautifulSoup

idx = 0

code_df = pd.read_html('http://kind.krx.co.kr/corpgeneral/corpList.do?method=download&searchType=13', header=0)[0] 
code_df.종목코드 = code_df.종목코드.map('{:06d}'.format) 
code_df = code_df[['회사명', '종목코드']]
code_df = code_df.rename(columns={'회사명': 'name', '종목코드': 'code'}) 

df2 = pd.DataFrame(columns = ['code', 'PER'])

# codecount = len(code_df)
codecount = 5

for i in range(0, codecount):
    try:
        if i%50 == 0:
            complete_ratio = round(i/codecount * 100, 1)
            print()
            print(str(i) + "/" + str(codecount) + "(" + str(complete_ratio) + "%) is completed")
            print()
        
        code = code_df['code'][i]

        # print(code)

        url = "https://finance.naver.com/item/main.nhn?code={code}".format(code=code)
        res = requests.get(url)
        soup = BeautifulSoup(res.content, 'lxml')
        # result = soup.find('em', id='_per')

        # PER_same_sector = soup.select('#tab_con1 > div:nth-child(6) > table > tbody > tr.strong > td > em')[0].text
        same_sector = soup.select('#tab_con1 > div:nth-child(6) > table > tbody > tr.strong > td > em')
        # tab_con1 > div:nth-child(6) > table > tbody > tr.strong > td > em
        print(same_sector)

        # print(result.text)
        # print(type(result.text))

        val_PER = float(result.text)

        if val_PER <= 10 :
            idx = len(df2) + 1
            df2.loc[idx] = [code, val_PER]
    except:
        pass

# print(df2)