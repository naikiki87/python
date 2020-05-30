import sys
from selenium import webdriver
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys
import pyperclip
import time

delay = 0.5


#클립보드에 input을 복사한 뒤
#해당 내용을 actionChain을 이용해 로그인 폼에 붙여넣기
def copy_input(xpath, input):
    pyperclip.copy(input)
    driver.find_element_by_xpath(xpath).click()
    ActionChains(driver).key_down(Keys.CONTROL).send_keys('v').key_up(Keys.CONTROL).perform()
    time.sleep(0.5)


id = 'naikiki87'
pw = 'k8mnaverso0'
toInput = 'naikiki87@naver.com'
# subject = '0000000'
subject = sys.argv[1]
# pw = '1!tndud2@'

# driver = webdriver.Chrome(r'C:\Users\smddu\Documents\chromedriver\chromedriver.exe')
driver = webdriver.Chrome('D:/temp/chromedriver.exe')
driver.implicitly_wait(3)

driver.get('https://nid.naver.com/nidlogin.login?mode=form&url=https%3A%2F%2Fwww.naver.com')
# driver.get('https://logins.daum.net/accounts/signinform.do?url=https%3A%2F%2Fwww.daum.net%2F')

copy_input('//*[@id="id"]', id)
time.sleep(delay)
copy_input('//*[@id="pw"]', pw)
# copy_input('//*[@id="inputPwd"]', pw)
time.sleep(delay)
driver.find_element_by_xpath('//*[@id="frmNIDLogin"]/fieldset/input').click()
# driver.find_element_by_xpath('//*[@id="loginBtn"]').click()

# driver.find_element_by_xpath('//*[@class="txt_pctop link_mail"]').click()
# driver.find_element_by_xpath('//*[@class="btn_comm btn_write"]').click()

driver.find_element_by_xpath('//*[@data-clk="svc.mail"]').click()

driver.find_element_by_xpath('//*[@class="btn_quickwrite _c1(mfCore|popupWrite|new) _ccr(lfw.write) _stopDefault"]').click()

copy_input('//*[@id="toInput"]', toInput)
copy_input('//*[@id="subject"]', subject)

driver.find_element_by_xpath('//*[@id="sendBtn"]').click()
time.sleep(delay)

driver.close()