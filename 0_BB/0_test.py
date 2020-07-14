# import pitcher

# p1 = pitcher.Pitcher(10)

# p1.test_func()

import pandas as pd 
import requests
import threading
import time
from bs4 import BeautifulSoup
import urllib.request

url = "http://www.kbreport.com/leader/pitcher/advanced?teamId=&pitcher_type=&year_from=&year_to=&split01=&split02_1=&split02_2=&inning_count=#/1"
source = requests.get(url)
# soup = BeautifulSoup(source.content, 'html.parser')
soup = BeautifulSoup(source.content, 'lxml')

# print(soup)
# print(soup.p.string)
# print(soup.find_all("tr"))
print(soup.find("td"))

# table = soup.find('table', {'class' : 'ltb-table iterative'})
# # table = soup.select('#resultListDiv > table')
# print(table)
# trs = table.find_all('tr')
# trs = soup.findAll('tr')
# print(len(trs))
# print(trs)
# data = soup.find('#resultListDiv > table > tbody > tr:nth-child(2) > td:nth-child(4)')
# print(data.get_text())
# data = soup.select('#resultListDiv > table > tbody > tr:nth-child(2) > td:nth-child(4)').text
# print(data)


# table = soup.find('table', {'class': 'grid'})
# trs = table.find_all('tr')
# for idx, tr in enumerate(trs): # enumerate를 사용하면 해당 값의 인덱스를 알 수 있다.
# if idx > 0:
# tds = tr.find_all('td')
# sequence = tds[0].text.strip() # 앞뒤 여백이 있어 strip()을 사용했다.
# description = tds[1].text.strip()
# solved_num = tds[2].text.strip()
# print(sequence, description, solved_num)