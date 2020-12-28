from pyspark import sql
from pyspark.sql import SparkSession, Row, functions as F, Window
from pyspark.sql.functions import when, col, expr, max, udf
from pyspark.sql.types import *
from errno import errorcode
import pandas as pd
import pymysql
import random
import time
import math
from pandas.api.types import is_numeric_dtype
from pandas.api.types import is_string_dtype

start_time = time.time()

# MySQL Connection 연결
conn = pymysql.connect(host='165.132.105.40', user='root', password='Elql27!^', db='projectBigdata', charset='utf8')
 
# Connection 으로부터 Cursor 생성
curs = conn.cursor()
curs.execute("delete from 2_detransaction")
conn.commit()
curs.execute("delete from 3_result_transaction")
conn.commit()
# curs.execute("select * from 1_basic_trans")
curs.execute("select * from 0_data_input")
conn.commit()
 
# # 데이타 Fetch
rows = curs.fetchall()
cnt_trans = len(rows)

sql_detrans = "insert into 2_detransaction(tid, uid, iid) values (%s, %s, %s)"

for a in range(cnt_trans) :
    tid = rows[a][0]
    uid = rows[a][1]

    items = rows[a][2].split(',')
    cnt_items = len(items)
    if cnt_items >= 1 :
        for b in range(cnt_items) :
            curs.execute(sql_detrans, (tid, uid, items[b]))
        conn.commit()
print("detrasaction complete")

### p_table 생성 및 초기화 
curs.execute("CREATE TABLE if not exists p_table (pid INTEGER NOT NULL, n integer not null, iid integer not null)")
conn.commit()
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

query = "select * from 2_detransaction"
input_df = spark.read.format('jdbc').options(
  driver=DRIVER,
  url=CONNECT_URL,
  query=query,
  user=CONNECT_USER,
  password=CONNECT_PWD).load()

print("2 : Raw data loading complete")

df_origin = input_df.select('*').toPandas()
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


    temp_result_2 = spark.sql(total_query).filter("cnt >= 2").collect()
    sql = "insert into p_table(pid, n, iid) values (%s, %s, %s)"
    cnt_temp_result_2 = len(temp_result_2)

    if cnt_temp_result_2 >= 1 :
        for k in range(cnt_temp_result_2) :
            for m in range(0, i+1, 1) :
                curs.execute(sql, (pid, i+1, temp_result_2[k][m]))
            pid = pid + 1
        conn.commit()
print("4-2 : Making p-table complete")

query = "select * from p_table"
df_p_table = spark.read.format('jdbc').options(
  driver=DRIVER,
  url=CONNECT_URL,
  query=query,
  user=CONNECT_USER,
  password=CONNECT_PWD).load().sort(col("pid").desc())


df_p = df_p_table.select('*').toPandas()
print("<< p Table >>")
print(df_p)

temp_tid_list = []
temp_pid_list = []

for i in range(len(df_origin)) :
    if df_origin.tid[i] not in temp_tid_list :
        temp_tid_list.append(df_origin.tid[i])

for i in range(len(df_p)) :
    if df_p.pid[i] not in temp_pid_list :
        temp_pid_list.append(df_p.pid[i])


print("5-1 : Diminishing raw data start")

df_merge = pd.DataFrame(columns=['tid','uid','iid','pid','n'])
pd_df_in = pd.DataFrame(columns=['tid','uid','iid'])
pd_df_not_in = pd.DataFrame(columns=['tid','uid','iid'])

for i in range(len(temp_tid_list)) :
    print(i, '/', len(temp_tid_list))
    temp_tid = temp_tid_list[i]
    temp_df_origin = df_origin[df_origin['tid'] == temp_tid]
    for j in range(len(temp_pid_list)) :
        temp_pid = temp_pid_list[j]
        temp_df_p = df_p[df_p["pid"] == temp_pid].copy()
        
        temp_df_p['iid'] = temp_df_p['iid'].astype(str)     ## 데이터 타입이 달라 동일하게 맞춰줌
        temp_temp = pd.merge(temp_df_origin, temp_df_p, how='right', on='iid')
        del(df_merge)
        df_merge = pd.DataFrame(columns=['tid','uid','iid','pid','n'])
        cnt_merge = 0
        for k in range(len(temp_temp)) :
            if not math.isnan(temp_temp.tid[k]) :
                cnt_merge = cnt_merge + 1

        cnt_p = temp_df_p.count()[0]

        if cnt_merge == cnt_p :
            temp_merge = pd.merge(temp_df_origin, temp_df_p, how='left', on='iid')

            for k in range(len(temp_merge)) :
                if math.isnan(temp_merge.pid[k]) :
                    pd_df_not_in.loc[len(pd_df_not_in)] = [temp_merge.tid[k], temp_merge.uid[k], temp_merge.iid[k]]
                else :
                    pd_df_in.loc[len(pd_df_in)] = [temp_merge.tid[k], temp_merge.uid[k], temp_merge.iid[k]]

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

pd_df_final = pd_df_final.sort_values(by=['tid'], axis=0)

print("final : ", pd_df_final)

temp_recover_tid_list

sql_input_res = "insert into 3_result_transaction(tid, uid, items) values (%s, %s, %s)"

for i in range(len(temp_recover_tid_list)) :
    target_tid = temp_recover_tid_list[i].tid

    items = []
    for j in range(len(pd_df_final)) :
        if pd_df_final.iloc[j][0] == target_tid :
            items.append(pd_df_final.iloc[j][2])
            uid = pd_df_final.iloc[j][1]

    items = list(map(str, items))
    input_item = ','.join(items)
    if input_item == '' :
        input_item = "12"
    print(target_tid, "input items : ", input_item)
    curs.execute(sql_input_res, (target_tid, uid, input_item))
    conn.commit()


conn.close()