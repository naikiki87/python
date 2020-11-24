import pymysql
 
# MySQL Connection 연결
conn = pymysql.connect(host='165.132.105.40', user='root', password='Elql27!^', db='projectBigdata', charset='utf8')
 
# Connection 으로부터 Cursor 생성
curs = conn.cursor()

curs.execute("delete from temp_testdata")
conn.commit()
 
# SQL문 실행
sql = "select * from basic_trans"
# sql = "CREATE TABLE p_table (id INTEGER NOT NULL PRIMARY KEY)"
curs.execute(sql)
conn.commit()
 
# # 데이타 Fetch
rows = curs.fetchall()
print(rows)     # 전체 rows

cnt_trans = len(rows)
print("len : ", cnt_trans)
print("items : ", rows[0][2], type(rows[0][2]))

sql = "insert into temp_testdata(tid, uid, iid) values (%s, %s, %s)"

for a in range(cnt_trans) :
    tid = rows[a][0]
    uid = rows[a][1]

    items = rows[a][2].split(',')
    print("items : ", items)

    cnt_items = len(items)

    print("cnt items : ", cnt_items)
    if cnt_items >= 1 :
        for b in range(cnt_items) :
            curs.execute(sql, (tid, uid, items[b]))
        conn.commit()
conn.close()