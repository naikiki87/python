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

index = 0
email = 0
delay = 0.5
item_slosh = []
driver = ''
email_time = 0
reqtime = 0

item = input("item : ")
unit_price = int(input("unit price : "))

def copy_input(xpath, input):
    global driver
    pyperclip.copy(input)
    driver.find_element_by_xpath(xpath).click()
    ActionChains(driver).key_down(Keys.CONTROL).send_keys('v').key_up(Keys.CONTROL).perform()
    time.sleep(0.5)

def setInterval(func):
    global index
    while index!=5:
        func()
        time.sleep(5)

def autoClick():
    pyautogui.click(x=918, y=468)

def getData():
    source = requests.get("http://polling.finance.naver.com/api/realtime.nhn?query=SERVICE_ITEM:005490|SERVICE_RECENT_ITEM:005490&_callback=")
    data = source.json()
    name = data['result']['areas'][0]['datas'][0]['nm']
    value = data['result']['areas'][0]['datas'][0]['nv']

    print(name, value)

def sendMail(subject):
    global driver
    loginid = 'naikiki87'
    loginpw = '1!tndud2@'
    toInput = 'naikiki87@daum.net'

    driver = webdriver.Chrome('D:/temp/chromedriver.exe')
    driver.implicitly_wait(3)
    driver.get('https://www.nate.com')

    copy_input('//*[@id="ID"]', loginid)
    time.sleep(0.3)
    copy_input('//*[@id="PASSDM"]', loginpw)
    time.sleep(0.3)
    driver.find_element_by_xpath('//*[@id="btnLOGIN"]').click()

    driver.find_element_by_xpath('//*[@class="mail"]').click()

    driver.find_element_by_xpath('//*[@class="write"]').click()

    time.sleep(1)

    copy_input('//*[@id="textArea_to"]', toInput)
    driver.find_element_by_xpath('//*[@class="subjectGuide"]').click()
    copy_input('//*[@class="txtbox"]', subject)

    driver.find_element_by_xpath('//*[@class="btn send"]').click()

    time.sleep(delay)

    driver.close()

def getData2():
    global email
    global unit_price
    global item
    global item_slosh
    global email_time
    global reqtime
    
    if email == 0:
        url = "http://polling.finance.naver.com/api/realtime.nhn?query=SERVICE_ITEM:"+ item +"|SERVICE_RECENT_ITEM:"+item+"&_callback="
        source = requests.get(url)

        data = source.json()
        name = data['result']['areas'][0]['datas'][0]['nm']
        value = data['result']['areas'][0]['datas'][0]['nv']

        print(reqtime)

        percent = (value - unit_price)/unit_price * 100
        # print("per : " + percent)
        print('per : %f' % (percent))

        time_duration = time.time() - email_time
        updown = ''

        if percent >= 3 or percent <= -3.5 :
            if percent >= 3 :
                updown = "up"
            else :
                updown = "down"

            if time_duration > 60 :
                email = 1
        
        if email == 1 :
            item2 = item + updown
            sendMail(item2)
            print("success")
            email_time = time.time()
            email = 0

        item_temp = [name, value]
        item_slosh = item_temp
        
        
        print(item_slosh)
        reqtime = reqtime + 1
        print()


setInterval(getData2)
