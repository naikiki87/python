import pandas as pd 
import requests
import threading
import time
from bs4 import BeautifulSoup

url = "http://www.historyexam.go.kr/mypage/exam/examAreaListPopup.do?pageIndex=1&testlevel=1&dspsn=N&lo_code=09&exam_area_code="
res = requests.post(url)
soup = BeautifulSoup(res.content, 'lxml')
# q1 = soup.select('#searchVO > div > div.won_pop_dv_tit_dv2.mar_tp30 > div:nth-child(4) > table > tbody > tr:nth-child(1) > td.no_b_right > img')[0].text
q1 = soup.select('#searchVO > div > div.won_pop_dv_tit_dv2.mar_tp30 > div:nth-child(4) > table > tbody > tr:nth-child(1) > td.no_b_right > img').alt

print(q1)

