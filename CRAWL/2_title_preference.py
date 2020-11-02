import pandas as pd 
import requests
import threading
import time
from bs4 import BeautifulSoup
import sys
import schedule

# pd.set_option('display.max_row', 20000)
# pd.set_option('display.max_columns', 10000)
pd.set_option('display.max_rows', None)
pd.set_option('display.max_columns', None)
pd.set_option('display.width', None)
pd.set_option('display.max_colwidth', -1)



NUM_PAGE = 20

def job() :
    df = pd.DataFrame(columns = ['title', 'count'])
    # df.style.set_properties(**{'text-align': 'right'})

    for i in range(NUM_PAGE):
        page = i * 30 + 1
        url = "http://mlbpark.donga.com/mp/b.php?p={page}&b=bullpen&id=202006130043772831&select=&query=&user=&site=donga.com&reply=&source=&sig=h6jRHl-gkh9RKfX2hgj9Sf-ghhlq".format(page = page)
        res = requests.get(url)
        soup = BeautifulSoup(res.content, 'lxml')

        topic = soup.findAll("span", class_="word_bullpen")
        title = soup.findAll("span", {"class" : "bullpen"})
        count = soup.findAll("span", {"class" : "viewV"})

        for j in range(len(title)):
            try :
                title_text = title[j].text.strip()
                # leng = len(title_text)
                # if title_text[leng-1] == ']' :


                if '[' in title[j].text :
                    if title[j].text[0] == '[' :
                        temp = 1
                    else :
                        t = title[j].text.index('[')
                        title_text = title[j].text[0:t].strip()
                
                if count[j].text == '0' or count[j].text == '1' or count[j].text == '2' or count[j].text == '3' or count[j].text == '4' or count[j].text == '5':
                    continue
                else :
                    df.loc[len(df)] = [title_text, count[j].text]
            except :
                pass

    df = df.sort_values(by=['count'])
    df = df.reset_index(drop=True)
    
    print("detecting")
    filename = 'basic_info.txt'
    f = open(filename,'w', encoding='utf8')
    sys.stdout = f
    print(df.head(20))
    sys.stdout = sys.__stdout__
    f.close()

# job()

schedule.every(1).minutes.do(job)

while True :
    schedule.run_pending()
    time.sleep(1)