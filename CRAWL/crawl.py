from selenium import webdriver
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys
import pyautogui
import pyperclip
import requests
import threading
import time
from bs4 import BeautifulSoup

index = 0
# item = ["005490", "005930"]
item = ["005490", "005930", "131370", "017180", "059090", "008350", "294140", "002720", "002360", "096530", "092190"]
# driver = webdriver.Chrome('D:/temp/chromedriver.exe')

def copy_input(xpath, input):
# def copy_input(xpath, input, driver):
    global driver
    pyperclip.copy(input)
    driver.find_element_by_xpath(xpath).click()
    ActionChains(driver).key_down(Keys.CONTROL).send_keys('v').key_up(Keys.CONTROL).perform()
    time.sleep(1)

def login():
    global driver
    loginid = 'naikiki87'
    loginpw = '1!tndud2@'

    # driver = webdriver.Chrome('D:/temp/chromedriver.exe')
    # driver.implicitly_wait(3)
    driver.get('https://logins.daum.net/accounts/signinform.do?url=https%3A%2F%2Fwww.daum.net%2F')

    copy_input('//*[@id="id"]', loginid)
    # copy_input('//*[@id="id"]', loginid, driver)
    time.sleep(0.3)
    copy_input('//*[@id="inputPwd"]', loginpw)
    # copy_input('//*[@id="inputPwd"]', loginpw, driver)
    time.sleep(0.3)
    driver.find_element_by_xpath('//*[@id="loginBtn"]').click()

def setInterval2(func, index2):
    global index
    while index!=5:
        if index==3:
            autoClick()
            break
        func(index2)
        index += 1
        time.sleep(1)

def autoClick():
    pyautogui.click(x=918, y=468)

def setInterval(func,time):
    e = threading.Event()
    while not e.wait(time):
        func()

def getData():
    source = requests.get("http://polling.finance.naver.com/api/realtime.nhn?query=SERVICE_ITEM:005490|SERVICE_RECENT_ITEM:005490&_callback=")
    data = source.json()
    name = data['result']['areas'][0]['datas'][0]['nm']
    value = data['result']['areas'][0]['datas'][0]['nv']

    print(name, value)

def getData2(index):
    print(index)

# setInterval(getData,0.5)
# setInterval2(getData2, 2)
login()