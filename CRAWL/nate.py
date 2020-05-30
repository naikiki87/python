from selenium import webdriver
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys
import pyautogui
import pyperclip
import requests
import threading
import time
from bs4 import BeautifulSoup

driver = webdriver.Chrome('D:/temp/chromedriver.exe')
toInput = "naikiki87@daum.net"
toTitle = "1234test"

def copy_input(xpath, input):
    global driver
    pyperclip.copy(input)
    driver.find_element_by_xpath(xpath).click()
    ActionChains(driver).key_down(Keys.CONTROL).send_keys('v').key_up(Keys.CONTROL).perform()
    time.sleep(0.5)

def login():
    global driver
    global toInput
    global toTitle
    loginid = 'naikiki87'
    loginpw = '1!tndud2@'

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
    copy_input('//*[@class="txtbox"]', toTitle)

    driver.find_element_by_xpath('//*[@class="btn send"]').click()

    time.sleep(delay)

    driver.close()

login()