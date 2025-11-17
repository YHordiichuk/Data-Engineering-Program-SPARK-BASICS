from pyspark.sql import SparkSession
from pyspark.sql.functions import col, udf, when, array, avg
from pyspark.sql.types import ArrayType, DoubleType, StringType
from encryption import PIIEncryptionService
from geocoding import GeocoderService
import pygeohash as ghsh
import os


OPENCAGE_API_KEY="xxx"
PII_ENCRYPTION_KEY="yyy"
 


s3_path_hotels = "s3a://m06awsbucket-g85pk5ly/m06sparkbasics/hotels/"
s3_path_weather = "s3a://m06awsbucket-g85pk5ly/m06sparkbasics/weather/"
result_s3_path = "s3a://m06awsbucket-g85pk5ly/m06sparkbasics/result/"

# local set up below
# OPENCAGE_API_KEY = os.getenv("OPENCAGE_API_KEY")
# PII_ENCRYPTION_KEY = os.getenv("PII_ENCRYPTION_KEY")
# AWS_ACCESS_KEY=os.getenv("AWS_ACCESS_KEY")
# AWS_SECRET_KEY=os.getenv("AWS_SECRET_KEY")
# spark = (
#     SparkSession.builder
#     .appName("S3SparkIntegration")
#     .master("local[*]")
#     .config("spark.jars.packages",
#             "org.apache.hadoop:hadoop-aws:3.3.4,"
#             "com.amazonaws:aws-java-sdk-bundle:1.12.367")
#     .config("spark.jars.repositories", "https://repo1.maven.org/maven2")
#     .config("spark.hadoop.fs.s3a.access.key", AWS_ACCESS_KEY) 
#     .config("spark.hadoop.fs.s3a.secret.key", AWS_SECRET_KEY)
#     .config("spark.hadoop.fs.s3a.impl", "org.apache.hadoop.fs.s3a.S3AFileSystem")
#     .config("spark.hadoop.fs.s3a.path.style.access", "true")
#     .config("spark.hadoop.fs.s3a.endpoint", "s3.eu-north-1.amazonaws.com")
#     .config("spark.driver.memory", "8g")
#     .config("spark.executor.memory", "8g")
#     .getOrCreate()
# )
spark = SparkSession.builder \
        .appName("ReadFromS3") \
        .config("spark.hadoop.fs.s3a.impl", "org.apache.hadoop.fs.s3a.S3AFileSystem") \
        .config("spark.hadoop.fs.s3a.aws.credentials.provider",
                "com.amazonaws.auth.WebIdentityTokenCredentialsProvider") \
        .config("spark.hadoop.fs.s3a.endpoint", "s3.amazonaws.com") \
        .getOrCreate()

geo_inst = GeocoderService(OPENCAGE_API_KEY)
pii_inst = PIIEncryptionService(PII_ENCRYPTION_KEY)

def ghsh_4(cord_list):
    try:
        lat,lng=cord_list
        if lat is not None and lng is not None:
            return ghsh.encode(lat, lng, precision=4)
        return None
    except Exception as e:
        return None
  

def get_lat_lng(address, city, country):
    lat, lng = geo_inst.get_cord(f"{address} {city}, {country}")
    return [float(lat), float(lng)]

ghsh_udf = udf(ghsh_4, StringType())

geo_udf = udf(get_lat_lng, ArrayType(DoubleType()))


df_hotels = spark.read.option("header", "true").csv(s3_path_hotels)
df_weather = spark.read.option("recursiveFileLookup", "true").parquet(s3_path_weather)

print(f"Count rows hotels {df_hotels.count()}")

df_hotels = df_hotels.withColumn("Latitude", col("Latitude").cast("double")) \
                     .withColumn("Longitude", col("Longitude").cast("double"))

df_missing = df_hotels.filter(
    (col("Latitude").isNull()) | (col("Latitude") == "") |
    (col("Longitude").isNull()) | (col("Longitude") == "")
).select("Id", "Address", "City", "Country").collect()

print(f"Count of null Lat\Lon {len(df_missing)}")

enriched_geo_results = []
for row in df_missing:
    lat, lng = geo_inst.get_cord(f"{row['Address']} {row['City']} {row['Country']}")
    if lat is not None and lng is not None:
        enriched_geo_results.append((row['Id'], float(lat), float(lng)))
df_geo_filled = spark.createDataFrame(enriched_geo_results, schema=["Id", "Latitude_filled", "Longitude_filled"])

print(f"Lat\Lon enriched via API")

df_hotels = (
    df_hotels
    .join(df_geo_filled, on="Id", how="left")
    .withColumn(
        "Latitude",
        when(col("Latitude").isNull() | (col("Latitude") == ""), col("Latitude_filled")).otherwise(col("Latitude"))
    )
    .withColumn(
        "Longitude",
        when(col("Longitude").isNull() | (col("Longitude") == ""), col("Longitude_filled")).otherwise(col("Longitude"))
    )
    .withColumn("geohash", ghsh_udf(array(col("Latitude"), col("Longitude"))))
    .drop("Latitude_filled", "Longitude_filled")
)

print(f"df_hotels geohash spark plan calculated")

df_weather = df_weather.withColumn("lat", col("lat").cast("double")) \
                     .withColumn("lng", col("lng").cast("double")) \
                    .withColumn("geohash", ghsh_udf(array(col("lat"), col("lng"))))

weather_agg = df_weather.groupBy("geohash").agg(
    avg("avg_tmpr_f").alias("avg_tmpr_f"),
    avg("avg_tmpr_c").alias("avg_tmpr_c")
)

print(f"df_weather geohash + aggregation spark plan calculated")
df_joined = df_hotels.join(weather_agg, on="geohash", how="left")


pii_inst = PIIEncryptionService(PII_ENCRYPTION_KEY)
df_encrypted = pii_inst.encrypt_pii_fields(df_joined, ["Name", "Address", "City", "Country"])


df_encrypted.repartition("Country", "City").write.mode("overwrite").parquet(result_s3_path)
print(f"Result written to S3 at {result_s3_path}")