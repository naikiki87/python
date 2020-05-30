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

    driver.find_element_by_xpath('//*[@class="txt_pctop link_mail"]').click()
    driver.find_element_by_xpath('//*[@class="btn_comm btn_write"]').click()

    # copy_input('//*[@id="toTextarea"]', toInput)
    copy_input('//*[@class="tf_address"]', toInput)
    # copy_input('//*[@id="tf_subject"]', toTitle)

    # driver.find_element_by_xpath('//*[@class="btn_toolbar btn_write"]').click()

login()