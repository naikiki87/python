from pyspark.sql import *

spark = SparkSession \
    .builder \
    .appName("Python Spark SQL basic example") \
    .config("spark.some.config.option") \
    .getOrCreate()
    
iris_df = spark.read.csv("iris.csv", inferSchema = True, header = True)

iris_df.show(5)