import requests
import threading
from bs4 import BeautifulSoup

cnt_0_digit = 0

item_code = "005930"

url = "https://finance.naver.com/item/main.nhn?code={}".format(item_code)
res = requests.get(url)
soup = BeautifulSoup(res.content, 'lxml')
result = soup.select('#_market_sum')[0].text.strip()
result = result.replace(',', '')
result = result.replace('\t', '')
result = result.replace('\n', '')

print("result : ", result)

nextstr = []
lensum = len(result)
ptr = 0
for k in range(0, lensum):
    if result[k] == '조':
        ptr = k
        break           
    nextstr.append(result[k])

if ptr != 0 :
    cnt_0_digit = 4 - (lensum - (ptr + 1))

    for m in range(0, cnt_0_digit) :
        nextstr.append('0')
    
    for n in range(ptr+1, lensum) :
        nextstr.append(result[n])

market_sum = int("".join(nextstr))

print("market sum : ", market_sum)

# return market_sum