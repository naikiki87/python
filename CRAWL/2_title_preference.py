import pandas as pd 
import requests
import threading
import time
from bs4 import BeautifulSoup

# url = "http://mlbpark.donga.com/mp/b.php?p=1&b=bullpen&id=202006130043772831&select=&query=&user=&site=donga.com&reply=&source=&sig=h6jRHl-gkh9RKfX2hgj9Sf-ghhlq"

for i in range(3):
    page = i * 30 + 1
    url = "http://mlbpark.donga.com/mp/b.php?p={page}&b=bullpen&id=202006130043772831&select=&query=&user=&site=donga.com&reply=&source=&sig=h6jRHl-gkh9RKfX2hgj9Sf-ghhlq".format(page = page)
    res = requests.get(url)
    soup = BeautifulSoup(res.content, 'lxml')

    # topic = soup.findAll("span", {"class" : "word_bullpen"})
    topic = soup.findAll("span", class_="word_bullpen")
    title = soup.findAll("span", {"class" : "bullpen"})
    count = soup.findAll("span", {"class" : "viewV"})
    print(title[0].text)

    for j in range(len(title)):
        # print(i, "/", j, " : ", title[j].text, count[j].text)
        print(i, "/", j, " : ", topic[j].text, count[j].text)