import pandas as pd 
import sys

pd.set_option('display.max_row', 20000)
pd.set_option('display.max_columns', 10000)

#해당 링크는 한국거래소에서 상장법인목록을 엑셀로 다운로드하는 링크입니다.
#다운로드와 동시에 Pandas에 excel 파일이 load가 되는 구조입니다.
stock_code = pd.read_html('http://kind.krx.co.kr/corpgeneral/corpList.do?method=download', header=0)[0] 
#stock_code.head()

# 데이터에서 정렬이 따로 필요하지는 않지만 테스트겸 Pandas sort_values를 이용하여 정렬을 시도해봅니다.
stock_code.sort_values(['상장일'], ascending=True)

# 필요한 것은 "회사명"과 "종목코드" 이므로 필요없는 column들은 제외
stock_code = stock_code[['회사명', '종목코드']] 

# 한글 컬럼명을 영어로 변경 
stock_code = stock_code.rename(columns={'회사명': 'company', '종목코드': 'code'}) 
#stock_code.head()

# 종목코드가 6자리이기 때문에 6자리를 맞춰주기 위해 설정해줌 
stock_code.code = stock_code.code.map('{:06d}'.format) 

# LG화학의 일별 시세 url 가져오기 
company='LG화학' 
code = stock_code[stock_code.company==company].code.values[0].strip() ## strip() : 공백제거
page = 1

url = 'http://finance.naver.com/item/sise_day.nhn?code={code}'.format(code=code)     
url = '{url}&page={page}'.format(url=url, page=page)
print(url)
df = pd.read_html(url, header=0)[0]
# df.head()

filename = "trend_anal.txt"
f = open(filename,'w', encoding='utf8')
sys.stdout = f
print(df)

sys.stdout = sys.__stdout__
f.close()

# company='LG화학' 
# code = stock_code[stock_code.company==company].code.values[0].strip() ## strip() : 공백제거

# df = pd.DataFrame()
# for page in range(1,21):
#     url = 'http://finance.naver.com/item/sise_day.nhn?code={code}'.format(code=code)     
#     url = '{url}&page={page}'.format(url=url, page=page)
#     print(url)
#     df = df.append(pd.read_html(url, header=0)[0], ignore_index=True)

# import matplotlib.pyplot as plt
# # 필요한 모듈 import 하기 
# import plotly
# import plotly.graph_objects as go
# import plotly.express as px

# # %matplotlib inline 은 jupyter notebook 사용자용 - jupyter notebook 내에 그래프가 그려지게 한다.
# %matplotlib inline 