from pyspark.sql import *

spark = SparkSession \
    .builder \
    .appName("Python Spark SQL basic example") \
    .config("spark.some.config.option") \
    .getOrCreate()
    
iris_df = spark.read.csv("iris.csv", inferSchema = True, header = True)

# iris_df.show(5)

iris_df.createOrReplaceTempView("iris")

spark.sql("SELECT * FROM iris LIMIT 5").show()