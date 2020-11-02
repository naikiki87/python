import collections
import requests
from bs4 import BeautifulSoup
import sys
import io
import pandas as pd
import re
import config
import schedule
import time
import datetime

# pd.set_option('display.max_row', 20000)
# pd.set_option('display.max_columns', 10000)
pd.set_option('display.max_rows', None)
pd.set_option('display.max_columns', None)
pd.set_option('display.width', None)
pd.set_option('display.max_colwidth', -1)

EXCEPT = config.EXCEPT
NUM_PAGE = 10

def job() :
    text_list = []
    for i in range(NUM_PAGE):
        page = i * 30 + 1
        url = "http://mlbpark.donga.com/mp/b.php?p={page}&b=bullpen&id=202006130043772831&select=&query=&user=&site=donga.com&reply=&source=&sig=h6jRHl-gkh9RKfX2hgj9Sf-ghhlq".format(page = page)
        res = requests.get(url)
        soup = BeautifulSoup(res.content, 'lxml')

        topic = soup.findAll("span", class_="word_bullpen")
        title = soup.findAll("span", {"class" : "bullpen"})
        count = soup.findAll("span", {"class" : "viewV"})

        for j in range(len(title)):
            title_text = title[j].text.strip()

            words = title_text.split(' ')
            if words[0] == '' :
                a = 1
            else :
                for j in range(len(words)) :
                    words[j] = words[j].strip()         # 공백 제거

                    if words[j] in EXCEPT : 
                        continue
                    elif words[j] != '' :
                        len_word = len(words[j])
                        if words[j][len_word-1] == "은" or words[j][len_word-1] == "는" or words[j][len_word-1] == "이" or words[j][len_word-1] == "가":
                            words[j] = words[j][0:len_word-1]

                        if words[j] in EXCEPT :
                            continue
                        else :
                            words[j] = re.sub('[0-9]+', '', words[j])
                            words[j] = re.sub('[A-Za-z]+', '', words[j])
                            words[j] = re.sub('[-=+,#/\?:^$.@*\"※~&%ㆍ·!』\\‘’|\(\)\[\]\<\>`\'…》]', '', words[j])
                            text_list.append(words[j])

    word_list = pd.Series(text_list)

    print("detecting")

    now = datetime.datetime.now()
    c_hour = now.strftime('%H')
    c_min = now.strftime('%M')
    c_sec = now.strftime('%S')
    str_time = c_hour + ':' + c_min + ':' + c_sec

    filename = 'word_info.txt'
    f = open(filename,'w', encoding='utf8')
    sys.stdout = f
    print("time : ", str_time)
    print(word_list.value_counts().head(20))
    sys.stdout = sys.__stdout__
    f.close()

# job()

schedule.every(30).seconds.do(job)

while True :
    schedule.run_pending()
    time.sleep(1)