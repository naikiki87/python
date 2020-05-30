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
# item = sys.argv[1]
# unit_price = int(sys.argv[2])
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
    id = 'naikiki87'
    pw = 'k8mnaverso0'
    toInput = 'naikiki87@daum.net'

    driver = webdriver.Chrome('D:/temp/chromedriver.exe')
    driver.implicitly_wait(3)
    driver.get('https://nid.naver.com/nidlogin.login?mode=form&url=https%3A%2F%2Fwww.naver.com')

    copy_input('//*[@id="id"]', id)
    time.sleep(delay)
    copy_input('//*[@id="pw"]', pw)
    time.sleep(delay)
    driver.find_element_by_xpath('//*[@id="frmNIDLogin"]/fieldset/input').click()
    driver.find_element_by_xpath('//*[@data-clk="svc.mail"]').click()
    driver.find_element_by_xpath('//*[@class="btn_quickwrite _c1(mfCore|popupWrite|new) _ccr(lfw.write) _stopDefault"]').click()
    copy_input('//*[@id="toInput"]', toInput)
    copy_input('//*[@id="subject"]', subject)
    driver.find_element_by_xpath('//*[@id="sendBtn"]').click()
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
