import numpy as np
import pandas as pd
from pyspark import sql
from pyspark.sql import SparkSession, Row, functions as F, Window
from pyspark.sql.functions import when, col, expr, max, udf
from pyspark.sql.types import IntegerType
from errno import errorcode
import pymysql

DRIVER_PATH = "C:/jdbc/mysql-connector-java-8.0.22.jar"

sc = SparkSession.builder.config("spark.driver.extraClassPath", DRIVER_PATH).getOrCreate()
spark = sql.SQLContext(sc)

# # Enable Arrow-based columnar data transfers
# spark.conf.set("spark.sql.execution.arrow.enabled", "true")

# Generate a pandas DataFrame
pdf = pd.DataFrame(np.random.rand(100, 3))

print("pdf : ", type(pdf))
print("pdf : ", pdf)

# Create a Spark DataFrame from a pandas DataFrame using Arrow
df = spark.createDataFrame(pdf)
print("df : ", type(df))
df.show()

# pdf.iloc[len(pdf)] = [1,2,3]
# print("pdf : ", pdf)

# df2 = spark.createDataFrame(pdf)
# df2.show()

# # Convert the Spark DataFrame back to a pandas DataFrame using Arrow
# result_pdf = df.select("*").toPandas()
# print("result : ", type(result_pdf))
# print("result : ", result_pdf)