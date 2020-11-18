from pyspark import sql
from pyspark.sql import SparkSession, Row, functions as F, Window
from pyspark.sql.functions import when, col, expr, max, udf
from pyspark.sql.types import *
from errno import errorcode
import pandas as pd
import pymysql
import random
import time

start_time = time.time()
 
conn = pymysql.connect(host='165.132.105.40', user='root', password='Elql27!^',
                       db='projectBigdata', charset='utf8')
curs = conn.cursor()
sql_create = "CREATE TABLE if not exists p_table \
(pid INTEGER NOT NULL, n integer not null, iid integer not null)"
curs.execute(sql_create)
conn.commit()

### p_table 초기화
curs.execute("delete from p_table")
conn.commit()

print("1 : Make p-table and initialize complete")

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

print("2 : Raw data loading complete")

pid = 0

pd_df_in = pd.DataFrame(columns = ['tid', 'uid', 'iid'])
pd_df_not_in = pd.DataFrame(columns = ['tid', 'uid', 'iid'])

### 최대 loop 수 탐색
input_df.registerTempTable("testdata")
spark.sql("SELECT tid,uid, COUNT(distinct iid) as countA FROM testdata GROUP BY tid,uid").registerTempTable("step1")
max_cnt = spark.sql("SELECT MAX(countA) as maxval from step1").first().asDict()['maxval']
print("3 : Counting Max Item Number : ", max_cnt)
print("4-1 : Making p-table start")

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

    # print(str(i+1) + "-item QUERY : ", total_query)

    temp_result_2 = spark.sql(total_query).filter("cnt >= 2").collect()
    sql = "insert into p_table(pid, n, iid) values (%s, %s, %s)"
    cnt_temp_result_2 = len(temp_result_2)

    if cnt_temp_result_2 >= 1 :
        for k in range(cnt_temp_result_2) :
            for m in range(0, i+1, 1) :
                curs.execute(sql, (pid, i+1, temp_result_2[k][m]))
            pid = pid + 1
        conn.commit()
conn.close()
print("4-2 : Making p-table complete")

query = "select * from p_table"
df_p = spark.read.format('jdbc').options(
  driver=DRIVER,
  url=CONNECT_URL,
  query=query,
  user=CONNECT_USER,
  password=CONNECT_PWD).load().sort(col("pid").desc()).registerTempTable("p_table")

temp_tid_list = spark.sql("select distinct tid from testdata").sort(col("tid").asc()).collect()
temp_pid_list = spark.sql("select distinct pid from p_table").sort(col("pid").desc()).collect()

print("5-1 : Diminishing raw data start")

for i in range(len(temp_tid_list)) :
    testdata_tid = temp_tid_list[i][0]
    for j in range(len(temp_pid_list)) :
        temp_pid = temp_pid_list[j][0]
        query = "SELECT t1.tid AS tid, t1.uid AS uid, t1.iid AS iid FROM (SELECT * FROM testdata WHERE tid = " + str(testdata_tid) + ") AS t1 right JOIN p_table ON t1.iid = p_table.iid WHERE p_table.pid = " + str(temp_pid) + " and tid IS NOT null"
        cnt = spark.sql(query).count()
        pid_cnt = spark.sql("select * from p_table where pid = " + str(temp_pid)).count()
        if cnt == pid_cnt :
            query_in = "SELECT t1.tid as tid, t1.uid as uid, t1.iid as iid FROM (SELECT * FROM testdata WHERE tid = " + str(testdata_tid) + ") AS t1 left outer JOIN (SELECT * from p_table WHERE pid = " + str(temp_pid) + ") AS p ON t1.iid = p.iid WHERE pid IS not null"
            query_not_in = "SELECT t1.tid as tid, t1.uid as uid, t1.iid as iid FROM (SELECT * FROM testdata WHERE tid = " + str(testdata_tid) + ") AS t1 left outer JOIN (SELECT * from p_table WHERE pid = " + str(temp_pid) + ") AS p ON t1.iid = p.iid WHERE pid IS null"

            temp_in = spark.sql(query_in).collect()
            temp_not_in = spark.sql(query_not_in).collect()

            for p in range(len(temp_in)) :
                in_tid = temp_in[p][0]
                in_uid = temp_in[p][1]
                in_iid = temp_in[p][2]

                pd_df_in.loc[len(pd_df_in)] = [in_tid, in_uid, in_iid]

            for m in range(len(temp_not_in)) :
                not_in_tid = temp_not_in[m][0]
                not_in_uid = temp_not_in[m][1]
                not_in_iid = temp_not_in[m][2]

                pd_df_not_in.loc[len(pd_df_not_in)] = [not_in_tid, not_in_uid, not_in_iid]

            break

print("5-2 : Diminishing raw data complete")
print("6-1 : Trans NOT-IN data start")

temp_recover_tid_list = input_df.select("tid").distinct().sort(col("tid").asc()).collect()
pd_df_final = pd.DataFrame(columns = ['tid', 'uid', 'iid'])

for i in range(len(temp_recover_tid_list)) :
    target_tid = temp_recover_tid_list[i].tid

    for j in range(len(pd_df_in)) :
        if pd_df_in.iloc[j].tid == target_tid :
            pd_df_final.loc[len(pd_df_final)] = [pd_df_in.iloc[j].tid, pd_df_in.iloc[j].uid, pd_df_in.iloc[j].iid]

    for k in range(len(pd_df_not_in)) : 
        if pd_df_not_in.iloc[k].tid == target_tid :
            trans_iid = str(pd_df_not_in.iloc[k].iid) + '/' + str(random.randint(10, 20)) + '/' + str(random.randint(20, 30))
            pd_df_final.loc[len(pd_df_final)] = [pd_df_not_in.iloc[k].tid, pd_df_not_in.iloc[k].uid, trans_iid]

print("6-2 : Trans NOT-IN data complete")

final_schema = StructType([ StructField("tid", IntegerType(), True)\
                       ,StructField("uid", IntegerType(), True)\
                       ,StructField("iid", StringType(), True)])
sparkdf_final = spark.createDataFrame(pd_df_final, schema=final_schema)
sparkdf_final.show()

# print("Time : ", time.time() - start_time)