import pymysql

test_db = pymysql.connect(
    user='root', 
    passwd='{설정한 비밀번호}', 
    host='127.0.0.1', 
    db='juso-db', 
    charset='utf8'
)