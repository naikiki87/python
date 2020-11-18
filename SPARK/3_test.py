from pyspark import sql
from pyspark.sql import SparkSession, Row, functions as F, Window
from pyspark.sql.functions import when, col, expr, max, udf
from pyspark.sql.types import IntegerType
from errno import errorcode
import pandas as pd
import pymysql
import random
 
conn = pymysql.connect(host='165.132.105.40', user='root', password='Elql27!^',
                       db='projectBigdata', charset='utf8')
curs = conn.cursor()
sql_create = "CREATE TABLE if not exists p_table \
(pid INTEGER NOT NULL, n integer not null, iid integer not null)"
curs.execute(sql_create)
conn.commit()

DRIVER_PATH = "C:/jdbc/mysql-connector-java-8.0.22.jar"
DRIVER = "com.mysql.jdbc.Driver"
CONNECT_URL = "jdbc:mysql://165.132.105.40:3306/projectBigdata?serverTimezone=Asia/Seoul"
CONNECT_USER = "root"
CONNECT_PWD = "Elql27!^"
sc = SparkSession.builder.config("spark.driver.extraClassPath", DRIVER_PATH).getOrCreate()
spark = sql.SQLContext(sc)

query = "select * from testdata"
input_df = spark.read.format('jdbc').options(
  driver=DRIVER,
  url=CONNECT_URL,
  query=query,
  user=CONNECT_USER,
  password=CONNECT_PWD).load()

pid = 0

pd_df_in = pd.DataFrame(columns = ['tid', 'uid', 'iid'])
pd_df_not_in = pd.DataFrame(columns = ['tid', 'uid', 'iid'])


### 최대 loop 수 탐색
input_df.registerTempTable("testdata")
c = spark.sql("SELECT tid,uid, COUNT(distinct iid) as countA FROM testdata GROUP BY tid,uid")
c.registerTempTable("step1")
max_cnt = spark.sql("SELECT MAX(countA) as maxval from step1").first().asDict()['maxval']

### p_table 초기화
sql = "delete from p_table"     
curs.execute(sql)
conn.commit()

for i in range(max_cnt) : 
    sel_query = "t1.iid as t1"
    gb_query = "GROUP BY t1.iid"
    join_query = ''
    if i == 0 :
        where_query = ''
    elif i >= 1 :
        where_query = "WHERE"
    for j in range(1, i+1, 1) :
        join_query = join_query + "JOIN testdata t" + str(j+1) + " ON t" + str(j+1) + ".tid = t" + str(j) + ".tid "
        where_query = where_query + " t" + str(j+1) + ".iid > t" + str(j) + ".iid AND"
        sel_query = sel_query + ", t" + str(j+1) + ".iid as t" + str(j+1)
        gb_query = gb_query + ", t" + str(j+1) + ".iid"

    if i >= 1 :
        where_query = where_query[0:len(where_query) - 3]       ## 마지막에 AND 문자열 제거

    total_query = "SELECT " + sel_query + ", COUNT(DISTINCT t1.uid) as cnt FROM testdata t1 " + join_query + where_query + gb_query

    print(str(i+1) + "-item QUERY : ", total_query)

    temp_result = spark.sql(total_query)
    temp_result.show()
    print("p중복성 만족")
    temp_result_2 = temp_result.filter("cnt >= 2")
    temp_result_2.show()
    
    sql = "insert into p_table(pid, n, iid) values (%s, %s, %s)"

    if temp_result_2.count() >= 1 :
        for k in range(temp_result_2.count()) :             ## row 갯수만큼 loop
            for m in range(0, i+1, 1) :                     ## n-item에서 n값만큼 loop
                curs.execute(sql, (pid, i+1, temp_result_2.collect()[k][m]))
            pid = pid + 1
        conn.commit()
conn.close()

query = "select * from p_table"
df_p = spark.read.format('jdbc').options(
  driver=DRIVER,
  url=CONNECT_URL,
  query=query,
  user=CONNECT_USER,
  password=CONNECT_PWD).load()

df_p.sort(col("pid").desc())

df_p.registerTempTable("p_table")

tid_list = spark.sql("select distinct tid from testdata")
temp_tid_list = tid_list.sort(col("tid").asc())

pid_list = spark.sql("select distinct pid from p_table")
temp_pid_list = pid_list.sort(col("pid").desc())

for i in range(temp_tid_list.count()) :
    testdata_tid = temp_tid_list.collect()[i].tid
    for j in range(temp_pid_list.count()) :
        temp_pid = temp_pid_list.collect()[j].pid
        query = "SELECT t1.tid AS tid, t1.uid AS uid, t1.iid AS iid FROM (SELECT * FROM testdata WHERE tid = " + str(testdata_tid) + ") AS t1 right JOIN p_table ON t1.iid = p_table.iid WHERE p_table.pid = " + str(temp_pid) + " and tid IS NOT null"
        
        cnt = spark.sql(query).count()
        pid_cnt = spark.sql("select * from p_table where pid = " + str(temp_pid)).count()
        if cnt == pid_cnt :
            print("query : ", query)
            print("tid : ", testdata_tid, "pid : ", temp_pid)
            print("transaction")
            spark.sql("select * from testdata where tid = " + str(testdata_tid )).show()
            print("p_table")
            spark.sql("select * from p_table where pid = " + str(temp_pid)).show()

            query_in = "SELECT t1.tid as tid, t1.uid as uid, t1.iid as iid FROM (SELECT * FROM testdata WHERE tid = " + str(testdata_tid) + ") AS t1 left outer JOIN (SELECT * from p_table WHERE pid = " + str(temp_pid) + ") AS p ON t1.iid = p.iid WHERE pid IS not null"
            query_not_in = "SELECT t1.tid as tid, t1.uid as uid, t1.iid as iid FROM (SELECT * FROM testdata WHERE tid = " + str(testdata_tid) + ") AS t1 left outer JOIN (SELECT * from p_table WHERE pid = " + str(temp_pid) + ") AS p ON t1.iid = p.iid WHERE pid IS null"

            temp_in = spark.sql(query_in)
            temp_not_in = spark.sql(query_not_in)

            for p in range(temp_in.count()) :
                in_tid = temp_in.collect()[p].tid
                in_uid = temp_in.collect()[p].uid
                in_iid = temp_in.collect()[p].iid

                pd_df_in.loc[len(pd_df_in)] = [in_tid, in_uid, in_iid]

            for m in range(temp_not_in.count()) :
                not_in_tid = temp_not_in.collect()[m].tid
                not_in_uid = temp_not_in.collect()[m].uid
                not_in_iid = temp_not_in.collect()[m].iid

                pd_df_not_in.loc[len(pd_df_not_in)] = [not_in_tid, not_in_uid, not_in_iid]

            break


print("df in : ", pd_df_in)
print("df not in : ", pd_df_not_in)

pd_df_final = pd.DataFrame(columns = ['tid', 'uid', 'iid'])

sparkdf_in = spark.createDataFrame(pd_df_in)
sparkdf_not_in = spark.createDataFrame(pd_df_not_in)

sparkdf_in.registerTempTable("p_in")
sparkdf_not_in.registerTempTable("p_not_in")

recover_tid_list = spark.sql("select distinct tid from p_in")
print("recover tid list")
recover_tid_list.show()
temp_recover_tid_list = recover_tid_list.sort(col("tid").asc())

for i in range(temp_recover_tid_list.count()) :
    target_tid = temp_recover_tid_list.collect()[i].tid

    list_in = spark.sql("select * from p_in where tid = " + str(target_tid))
    print("list in")
    list_in.show()
    for j in range(list_in.count()) :
        print("list in")
        in_tid = list_in.collect()[j].tid
        in_uid = list_in.collect()[j].uid
        in_iid = list_in.collect()[j].iid

        pd_df_final.loc[len(pd_df_final)] = [in_tid, in_uid, in_iid]

        print("final : ", pd_df_final)

    list_not_in = spark.sql("select * from p_not_in where tid = " + str(target_tid))
    print("list not in")
    list_not_in.show()
    for k in range(list_not_in.count()) :
        print("list not in")
        not_in_tid = list_not_in.collect()[k].tid
        not_in_uid = list_not_in.collect()[k].uid
        not_in_iid = list_not_in.collect()[k].iid

        trans_iid = str(not_in_iid) + '/' + str(random.randint(10, 20)) + '/' + str(random.randint(20, 30))

        print("trans : ", trans_iid)

        pd_df_final.loc[len(pd_df_final)] = [not_in_tid, not_in_uid, trans_iid]

        print("final2 : ", pd_df_final)

# print("final : ", pd_df_final)
sparkdf_final = spark.createDataFrame(pd_df_final)
sparkdf_final.show()