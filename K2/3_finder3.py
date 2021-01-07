import pandas as pd

code = "005930"
url = 'http://finance.naver.com/item/sise_day.nhn?code={code}'.format(code=code) 
table = pd.read_html(url, header=0)
print(table)

# print(soup)


# import requests
# import pandas as pd
# import json
# from pandas.io.json import json_normalize
# from bs4 import BeautifulSoup

# url = 'https://stationdata.wunderground.com/cgi-bin/stationlookup?station=KMAHADLE7&units=both&v=2.0&format=json&callback=jQuery1720724027235122559_1542743885014&_=15'
# res = requests.get(url)
# soup = BeautifulSoup(res.content, "lxml")
# s = soup.select('html')[0].text.strip('jQuery1720724027235122559_1542743885014(').strip(')')
# s = s.replace('null','"placeholder"')
# data= json.loads(s)
# data = json_normalize(data)
# df = pd.DataFrame(data)
# print(df)


# code = "005930"
# url = 'https://finance.naver.com/item/sise_day.nhn?code='+code
# r = requests.get(url)
# html = r.content
# soup = BeautifulSoup(html, 'html.parser')
# table = soup.select('table')

# print(table)