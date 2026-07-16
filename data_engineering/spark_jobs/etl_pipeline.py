import os
from pyspark.sql import SparkSession
from pyspark.sql.functions import col, from_json, current_timestamp
from pyspark.sql.types import StructType, StructField, StringType, IntegerType, DoubleType, DateType

# Configuration
KAFKA_BROKER = os.environ.get("KAFKA_BROKER", "kafka:29092")
POSTGRES_USER = os.environ.get("POSTGRES_USER", "postgres")
POSTGRES_PASSWORD = os.environ.get("POSTGRES_PASSWORD", "postgres")
POSTGRES_DB = os.environ.get("POSTGRES_DB", "healthsphere_ai")
POSTGRES_HOST = os.environ.get("POSTGRES_HOST", "postgres")
POSTGRES_URL = f"jdbc:postgresql://{POSTGRES_HOST}:5432/{POSTGRES_DB}"

def get_spark_session():
    return SparkSession.builder \
        .appName("HealthSphere ETL Pipeline") \
        .config("spark.jars.packages", "org.apache.spark:spark-sql-kafka-0-10_2.12:3.5.0,org.postgresql:postgresql:42.6.0") \
        .getOrCreate()

# Schemas based on CSV headers
air_quality_schema = StructType([
    StructField("Record_ID", StringType(), True),
    StructField("City", StringType(), True),
    StructField("Date", StringType(), True),
    StructField("AQI", DoubleType(), True),
    StructField("PM2_5", DoubleType(), True),
    StructField("PM10", DoubleType(), True),
    StructField("Humidity", DoubleType(), True),
    StructField("Temperature_C", DoubleType(), True),
    StructField("NO2", DoubleType(), True),
    StructField("SO2", DoubleType(), True)
])

fitness_schema = StructType([
    StructField("Record_ID", StringType(), True),
    StructField("User_ID", StringType(), True),
    StructField("Date", StringType(), True),
    StructField("Steps", IntegerType(), True),
    StructField("Calories_Burned", DoubleType(), True),
    StructField("Distance_km", DoubleType(), True),
    StructField("Sleep_Hours", DoubleType(), True),
    StructField("Resting_Heart_Rate", DoubleType(), True),
    StructField("Active_Minutes", DoubleType(), True),
    StructField("Floors_Climbed", IntegerType(), True)
])

health_schema = StructType([
    StructField("User_ID", StringType(), True),
    StructField("Age", IntegerType(), True),
    StructField("Gender", StringType(), True),
    StructField("Height_cm", DoubleType(), True),
    StructField("Weight_kg", DoubleType(), True),
    StructField("Systolic_BP", DoubleType(), True),
    StructField("Diastolic_BP", DoubleType(), True),
    StructField("Fasting_Blood_Sugar", DoubleType(), True),
    StructField("HbA1c", DoubleType(), True),
    StructField("Smoking", StringType(), True),
    StructField("Alcohol", StringType(), True),
    StructField("Sleep_Hours", DoubleType(), True),
    StructField("Exercise_Frequency", StringType(), True),
    StructField("Daily_Calories", DoubleType(), True),
    StructField("Sugar_Intake_g", DoubleType(), True),
    StructField("Family_History_Diabetes", StringType(), True),
    StructField("BMI", DoubleType(), True),
    StructField("Diabetes_Risk", StringType(), True)
])

def write_to_postgres(df, epoch_id, table_name, schema_fields):
    # Log unknown columns if any (since we extracted raw_json)
    # This is a bit tricky in pure Spark without collecting, but we can do a quick check on the first row
    try:
        first_row = df.select("raw_json").first()
        if first_row:
            import json
            raw_data = json.loads(first_row["raw_json"])
            unmapped = set(raw_data.keys()) - set(schema_fields)
            if unmapped:
                print(f"[{table_name}] Unmapped columns detected and ignored: {unmapped}")
    except Exception as e:
        pass # Do not crash

    # Drop the raw_json column before writing
    cleaned_df = df.drop("raw_json").dropDuplicates()
    
    cleaned_df.write \
        .format("jdbc") \
        .option("url", POSTGRES_URL) \
        .option("dbtable", table_name) \
        .option("user", POSTGRES_USER) \
        .option("password", POSTGRES_PASSWORD) \
        .option("driver", "org.postgresql.Driver") \
        .mode("append") \
        .save()

def process_stream(spark, topic, schema, table_name):
    print(f"Starting stream for topic {topic}")
    
    df = spark \
        .readStream \
        .format("kafka") \
        .option("kafka.bootstrap.servers", KAFKA_BROKER) \
        .option("subscribe", topic) \
        .option("startingOffsets", "earliest") \
        .option("failOnDataLoss", "false") \
        .load()

    # Keep raw_json to check for unmapped columns later
    parsed_df = df.withColumn("raw_json", col("value").cast("string")) \
                  .withColumn("data", from_json(col("raw_json"), schema)) \
                  .select("raw_json", "data.*")
    
    final_df = parsed_df.withColumn("created_at", current_timestamp())
    schema_fields = [f.name for f in schema.fields]

    query = final_df.writeStream \
        .foreachBatch(lambda df, epoch_id: write_to_postgres(df, epoch_id, table_name, schema_fields)) \
        .outputMode("append") \
        .start()
    
    return query

if __name__ == "__main__":
    import json
    spark = get_spark_session()
    
    # Load configuration
    config_path = os.path.join(os.path.dirname(__file__), "datasets_config.json")
    try:
        with open(config_path, "r") as f:
            config = json.load(f)
    except Exception as e:
        print(f"Failed to load datasets_config.json: {e}")
        config = {"datasets": []}
        
    schema_map = {
        "air_quality": air_quality_schema,
        "fitness": fitness_schema,
        "health": health_schema
    }
    
    queries = []
    for dataset in config.get("datasets", []):
        topic = dataset["topic"]
        table_name = dataset["table_name"]
        schema_type = dataset["schema_type"]
        
        schema = schema_map.get(schema_type)
        if not schema:
            print(f"Warning: No schema defined for {schema_type}. Skipping {topic}.")
            continue
            
        q = process_stream(spark, topic, schema, table_name)
        queries.append(q)
        
    if queries:
        spark.streams.awaitAnyTermination()
    else:
        print("No valid dataset streams configured.")
