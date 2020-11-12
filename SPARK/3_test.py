from pyspark import sql
from pyspark.sql import SparkSession, Row, functions as F, Window
from pyspark.sql.functions import when, col, expr, max, udf
from pyspark.sql.types import IntegerType

DRIVER_PATH = "C:/jdbc/mysql-connector-java-8.0.22.jar"
DRIVER = "com.mysql.jdbc.Driver"
CONNECT_URL = "jdbc:mysql://165.132.105.40:3306/projectBigdata?serverTimezone=Asia/Seoul"
CONNECT_USER = "root"
CONNECT_PWD = "Elql27!^"
sc = SparkSession.builder.config("spark.driver.extraClassPath", DRIVER_PATH).getOrCreate()
spark = sql.SQLContext(sc)

sql = "select * from testdata"

input_df = spark.read.format('jdbc').options(
  driver=DRIVER,
  url=CONNECT_URL,
  query=sql,
  user=CONNECT_USER,
  password=CONNECT_PWD).load()

# input_df.show()                     ## raw data
# input_df.select("tid", "uid").show()
# input_df.groupBy("tid").count().show()
# temp = input_df.groupBy("tid").count()    ## groupby tid and counting
# temp.registerTempTable("df_table")
# a = spark.sql("SELECT MAX(count) as maxval FROM df_table").first().asDict()['maxval']      ## get max count
# print("a : ", a)

# b = spark.sql("SELECT MAX(count) as maxval FROM df_table")
# b.show()

input_df.registerTempTable("testdata")
c = spark.sql("SELECT tid,uid, COUNT(distinct iid) as countA FROM testdata GROUP BY tid,uid")
c.registerTempTable("step1")
d = spark.sql("SELECT MAX(countA) as maxval from step1").first().asDict()['maxval']
# c.show()
print("max : ", d)

for i in range(d) : 
    sel_query = "t1.iid"
    gb_query = "GROUP BY t1.iid"
    join_query = ''
    if i == 0 :
        where_query = ''
    elif i >= 1 :
        where_query = "WHERE"
    for j in range(1, i+1, 1) :
        join_query = join_query + "JOIN testdata t" + str(j+1) + " ON t" + str(j+1) + ".tid = t" + str(j) + ".tid "
        where_query = where_query + " t" + str(j+1) + ".iid > t" + str(j) + ".iid AND"
        sel_query = sel_query + ", t" + str(j+1) + ".iid"
        gb_query = gb_query + ", t" + str(j+1) + ".iid"

    if i >= 1 :
        where_query = where_query[0:len(where_query) - 3]       ## 마지막에 AND 문자열 제거

    total_query = "SELECT " + sel_query + ", COUNT(DISTINCT t1.uid) FROM testdata t1 " + join_query + where_query + gb_query

    print("QUERY : ", total_query)

    spark.sql(total_query).show()

# fp_1 = spark.sql("SELECT t1.iid, count(distinct uid) FROM testdata t1 GROUP BY t1.iid")
# fp_1.show()

# fp_2 = spark.sql("SELECT t1.iid, t2.iid, COUNT(DISTINCT t1.uid) FROM testdata t1 JOIN testdata t2 ON t1.tid = t2.tid WHERE t2.iid > t1.iid GROUP BY t1.iid, t2.iid")
# fp_2.show()

# fp_3 = spark.sql("SELECT t1.iid, t2.iid, t3.iid, COUNT(DISTINCT t1.uid) FROM testdata t1 JOIN testdata t2 ON t1.tid = t2.tid join testdata t3 ON t3.tid = t2.tid WHERE t3.iid > t2.iid AND t2.iid > t1.iid GROUP BY t1.iid, t2.iid, t3.iid")
# fp_3.show()
# # fp_3 = spark.sql("SELECT t1.iid, t2.iid, t3.iid, COUNT(DISTINCT t1.uid) FROM testdata t1 JOIN testdata t2 ON t1.tid = t2.tid join testdata t3 ON t3.tid = t2.tid WHERE t2.iid > t1.iid AND t3.iid > t2.iid GROUP BY t1.iid, t2.iid, t3.iid")
# # fp_3.show()

# fp_4 = spark.sql("SELECT t1.iid, t2.iid, t3.iid, t4.iid, COUNT(DISTINCT t1.uid) FROM testdata t1 JOIN testdata t2 ON t1.tid = t2.tid join testdata t3 ON t3.tid = t2.tid JOIN testdata t4 ON t4.tid = t3.tid WHERE t4.iid > t3.iid AND t3.iid > t2.iid AND t2.iid > t1.iid GROUP BY t1.iid, t2.iid, t3.iid, t4.iid")
# fp_4.show()
# # fp_4 = spark.sql("SELECT t1.iid, t2.iid, t3.iid, t4.iid, COUNT(DISTINCT t1.uid) FROM testdata t1 JOIN testdata t2 ON t1.tid = t2.tid join testdata t3 ON t3.tid = t2.tid JOIN testdata t4 ON t4.tid = t3.tid WHERE t2.iid > t1.iid AND t3.iid > t2.iid AND t4.iid > t3.iid GROUP BY t1.iid, t2.iid, t3.iid, t4.iid")
# # fp_4.show()
# input_df.groupBy("tid", "uid").count("iid").distinct().show()

# input_df.groupBy("tid", "uid").select("tid", "uid").show()

# input_df.select("a").show()

# input_df.filter(input_df("a") >= 10).show()
# input_df.filter("a > 10").show()

# input_df.groupBy("tid").count().show()


# print("type : ", type(input_df))
# df1 = input_df
# df1.count()
# df1.show()

# 테이블 생성
# create new table and insert query execution result
# input_df.write.format('jdbc').options(
#   driver=DRIVER,
#   url=CONNECT_URL,
#   dbtable="test2",
#   user=CONNECT_USER,
#   password=CONNECT_PWD).mode('overwrite').save()