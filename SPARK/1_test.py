import pandas as pd
import spark as spark
from pyspark.shell import sqlContext
from pyspark.sql import *

# df = pd.DataFrame({'numbers': [1, 2, 3], 'colors': ['red', 'white', 'blue']})
#
# print("df : ", df)



# from pyspark.sql import SQLContext, SparkSession

# from pyspark.sql.functions import col, initcap, length, desc, udf, when, lower

# spark = SparkSession.builder.appName("prasadad").master('local').config('spark.driver.extraClassPath', 'C:\spark\spark-3.0.1-bin-hadoop2.7\jars\mariadb-java-client-2.6.0.jar').getOrCreate() sc = spark.sparkContext  sqlContext = SQLContext(sc)  df = sqlContext.read.format("jdbc") \
#     .options(url="jdbc:mariadb://165.132.105.42:3306/spark",driver="org.mariadb.jdbc.Driver",dbtable="test1",user="root",password="elql2716") \
#     .load()

spark = SparkSession \
    .builder \
    .appName("Python Spark SQL basic example") \
    .config("spark.some.config.option") \
    .getOrCreate()

df = spark.read.csv("iris.csv", inferSchema = True, header = True)

# print("df :", df.info())
# print("df :", df)

df.registerTempTable("tmp_test")
numDF = sqlContext.sql("select variety from tmp_test")
# numDF.show()
print("numDF : ", numDF)