import pandas as pd 
import requests
import threading
import time
from bs4 import BeautifulSoup

url = "https://www.kovo.co.kr/stats/43001_player-totalrecord.asp?s_part=1&spart=&t_code=&s_season=017&s_pr=201%7C1&e_season=017&e_pr=201%7C2&part=s"
res = requests.post(url)
soup = BeautifulSoup(res.content, 'lxml')
# print("soup : ", soup)
# q1 = soup.select('#tab1 > div.wrp_lst > table > tbody > tr:nth-of-type(1)')
# print(q1)

# table = soup.select('#tab1 > div.wrp_lst > table > tbody')
# trs = table.find_all('tr')
# print(type(table))
# print(table[0])
# print("len : ", len(table))
# print(trs)

table = soup.find("table", {"class": "lst_board"})
tbody = table.find('tbody')
tr = tbody.find_all('tr')[0]
trs = tbody.find_all("tr", {"class" : ""})
print(trs)
# print("len : ", len(trs))
# print("data : ", tr)
# print("type : ", type(tr))
# tbody = table.find('tbody')

# trs = tbody.find_all('tr')

# # print(trs)
# print("len : ", len(trs))

# for tr in trs :
#     try :
#         tds = tr.find_all('td')
#         print("tds : ", tds)
#     except :
#         pass
