import pymysql
 
# MySQL Connection 연결
conn = pymysql.connect(host='165.132.105.40', user='root', password='Elql27!^',
                       db='projectBigdata', charset='utf8')
 
# Connection 으로부터 Cursor 생성
curs = conn.cursor()
 
# SQL문 실행
# sql = "select * from testdata"
sql = "CREATE TABLE p_table (id INTEGER NOT NULL PRIMARY KEY)"
curs.execute(sql)
conn.commit()
 
# # 데이타 Fetch
# rows = curs.fetchall()
# print(rows)     # 전체 rows
 
# # Connection 닫기
conn.close()