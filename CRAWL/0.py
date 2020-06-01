from selenium import webdriver
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys
import pyautogui
import pyperclip
import requests
import threading
import time
from bs4 import BeautifulSoup
import sys

testt = 0

index = 0
talk = 0
heartbeat = 0
delay = 0.5
item_slosh = []
driver = ''
talk_time = 0
hb_time = 0
reqtime = 0

limitup = 3
limitdown = -3.5

item = input("item : ")

url = "http://polling.finance.naver.com/api/realtime.nhn?query=SERVICE_ITEM:"+ item +"|SERVICE_RECENT_ITEM:"+item+"&_callback="
source = requests.get(url)
data = source.json()
name = data['result']['areas'][0]['datas'][0]['nm']

print(name)

unit_price = int(input("unit price : "))
# itemno = int(input("item counter : "))

def setInterval(func):
    global index
    while index!=5:
        func()
        time.sleep(5)

def sendkakao(text):
    pyperclip.copy(text)
    pyautogui.click(x=1609, y=958)
    time.sleep(delay)
    
    pyautogui.hotkey("ctrl","v")
    # pyautogui.typewrite(text)
    pyautogui.press('enter')

def getData2():
    global talk
    global heartbeat
    global unit_price
    global item
    global item_slosh
    global talk_time
    global hb_time
    global reqtime
    
    if talk == 0:
        url = "http://polling.finance.naver.com/api/realtime.nhn?query=SERVICE_ITEM:"+ item +"|SERVICE_RECENT_ITEM:"+item+"&_callback="
        source = requests.get(url)

        data = source.json()
        name = data['result']['areas'][0]['datas'][0]['nm']
        value = data['result']['areas'][0]['datas'][0]['nv']

        # print(reqtime)

        percent = (value - unit_price)/unit_price * 100
        # print("per : " + str(round(percent, 2)) + "%")
        # print('per : %f' % (percent))

        time_duration = time.time() - talk_time
        hb_duration = time.time() - hb_time
        updown = ''

        r_time = time.localtime()
        rmin = ""

        # 주기적 alarm
        if r_time.tm_hour >= 9 and r_time.tm_hour <= 15:
            if r_time.tm_min == 0 or r_time.tm_min == 15 or r_time.tm_min == 30 or r_time.tm_min == 45:
                if hb_duration > 60 :
                    if r_time.tm_min == 0:
                        rmin = "00"
                    if r_time.tm_min == 15:
                        rmin = "15"
                    if r_time.tm_min == 30:
                        rmin = "30"
                    if r_time.tm_min == 45:
                        rmin = "45"
                    heartbeat = 1
        
        if heartbeat == 1:
            item2 = "[" + rmin + "] " + item + " " + name + " : " + str(round(percent, 2)) + "%"
            print(item2)
            sendkakao(item2)
            hb_time = time.time()
            heartbeat = 0

        if percent >= limitup or percent <= limitdown :
            if percent >= limitup :
                # updown = "[↑]" + str(percent) + "%"
                updown = "[▲]"
                print("up")
            else :
                print("down")
                updown = "[▼]"
                # updown = " DOWN " + str(percent) + "%"
            if time_duration > 60 :
                talk = 1
        
        if talk == 1 :
            if r_time.tm_hour >= 9 and r_time.tm_hour <= 16:
                percent = round(percent, 2)
                item2 = updown + item + " " + name + " : " + str(percent) + "%"
                print("name" + name)
                print(item2)
                sendkakao(item2)
                print("success")
                talk_time = time.time()
                talk = 0

        item_slosh = [item, name, unit_price, value]

        if reqtime == 1000 :
            reqtime = 0

        if reqtime < 10 :
            seq = "000"+str(reqtime)
        elif reqtime < 100 :
            seq = "00"+str(reqtime)
        elif reqtime < 1000 :
            seq = "0"+str(reqtime)
        
        print(seq + " " + str(item_slosh) + " " + "per : " + str(round(percent, 2)) + "%")
        # print("per : " + str(round(percent, 2)) + "%")
        reqtime = reqtime + 1

setInterval(getData2)
