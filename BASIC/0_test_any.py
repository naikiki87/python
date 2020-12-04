import sys
import random
import time
import datetime
import sqlite3
from PyQt5.QtCore import *
from PyQt5 import QtTest, QtCore, QtWidgets
import pandas as pd 
import requests
import threading
from bs4 import BeautifulSoup

SUBS_CNT = 200

SHOW_SCALE = 5
VOL_FIN_PAGE = 5    # 평균 volume을 구할 표본 수 -> 1 당 10일치


code_df = pd.read_html('http://kind.krx.co.kr/corpgeneral/corpList.do?method=download&searchType=13', header=0)[0] 
code_df.종목코드 = code_df.종목코드.map('{:06d}'.format) 
code_df = code_df[['회사명', '종목코드']]
code_df = code_df.rename(columns={'회사명': 'name', '종목코드': 'code'}) 

df_last = pd.DataFrame(columns = ['code', 'p_avr', 'stdev'])

# code_df2 = pd.DataFrame(columns={'name', 'code'}) 
code_df2 = []

for i in range(2000) :
    try :
        code_df2.append(code_df.code[i])
    except:
        pass
print(code_df2)

# rand_index = [random.randint(0, len(code_df)) for r in range(SUBS_CNT)]

# for i in range(SUBS_CNT) :
#     try :
#         code_df2.append(code_df.code[rand_index[i]])
#         # code_df2.loc[i] = code_df.loc[rand_index[i]]
#     except :
#         pass

# print(code_df2)

