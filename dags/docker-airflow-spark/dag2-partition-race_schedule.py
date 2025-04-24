from airflow import DAG
from airflow.operators.empty import EmptyOperator
from airflow.operators.python import PythonOperator
from airflow.providers.google.cloud.hooks.gcs import GCSHook

import os
import glob
import shutil
from datetime import datetime, timedelta
import pathlib
from pyspark.sql import SparkSession
# from pyspark.sql import functions as F
from pyspark.sql.functions import year, month, col
from pyspark.sql import types
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
# Define GCS bucket as input data
GCS_BUCKET_NAME = os.getenv('GCS_BUCKET_NAME')
GCP_CONN_ID = os.getenv('GCP_CONN_ID')
RATE_LIMIT_DELAY = float(os.getenv("RATE_LIMIT_DELAY", 1))
DESTINATION_BUCKET = os.getenv('DESTINATION_BUCKET')
BASE_DESTINATION_PATH = os.getenv('BASE_DESTINATION_PATH')

def init_spark():
    spark = SparkSession.builder \
        .appName("F1RaceResultsCSVtoParquet") \
        .config("spark.jars", "/opt/airflow/config/gcs-connector-hadoop3-latest.jar") \
        .getOrCreate()
    
    spark._jsc.hadoopConfiguration().set("google.cloud.auth.service.account.json.keyfile", 
                                         "/opt/airflow/credentials/<insert_sample_gcp_credentials>")
    spark._jsc.hadoopConfiguration().set("fs.gs.impl", 
                                         "com.google.cloud.hadoop.fs.gcs.GoogleHadoopFileSystem")
    spark._jsc.hadoopConfiguration().set("fs.AbstractFileSystem.gs.impl", 
                                         "com.google.cloud.hadoop.fs.gcs.GoogleHadoopFS")
    
    return spark

def load_parquet_to_gcs(parquet_file_path, **kwargs):
    try:
        spark = init_spark()

        bucket_name = kwargs.get("bucket_name", GCS_BUCKET_NAME)
        destination_bucket = kwargs.get("destination_bucket", DESTINATION_BUCKET)
        gcp_conn_id = kwargs.get("gcp_conn_id", GCP_CONN_ID)
        base_destination_path = kwargs.get("base_destination_path", BASE_DESTINATION_PATH)
        input_filename = "race_schedule_2020.csv"
        input_blob_path = f"gs://{bucket_name}/{base_destination_path}/{input_filename}"
        
        if not bucket_name:
            raise ValueError("GCS Bucket name is missing!")
        if not gcp_conn_id:
            raise ValueError("GCP Connection ID is missing!")
        if not input_blob_path:
            raise ValueError("GCP object name as input is missing!")
        
        race_result_schema = types.StructType([
            types.StructField("raceResultId", types.IntegerType(), True),
            types.StructField("driverId", types.StringType(), True),
            types.StructField("season", types.IntegerType(), True),
            types.StructField("round", types.IntegerType(), True),
            types.StructField("raceName", types.StringType(), True),
            types.StructField("date", types.DateType(), True),
            types.StructField("driverName", types.StringType(), True),
            types.StructField("constructorId", types.StringType(), True),
            types.StructField("constructorName", types.StringType(), True),
            types.StructField("grid", types.IntegerType(), True),
            types.StructField("position", types.IntegerType(), True),
            types.StructField("points", types.IntegerType(), True),
            types.StructField("status", types.StringType(), True),
            types.StructField("laps", types.IntegerType(), True),
            types.StructField("fastest_rank", types.IntegerType(), True),
            types.StructField("fastest_lap", types.IntegerType(), True),
            types.StructField("fastest_time", types.DoubleType(), True),
            types.StructField("fastest_speed", types.DoubleType(), True)
        ])

        df = spark.read.option("header", "true").schema(race_result_schema).csv(input_blob_path)

        df = df.withColumn("race_date", col("date")) \
               .withColumn("year", year(col("date"))) \
               .withColumn("month", month(col("date")))

        year_month = df.select("year", "month").distinct().collect()
        parquet_files = []

        for row in year_month:
            year_val = row["year"]
            month_val = row["month"]
            local_output_path = f"{parquet_file_path}/race_result_{year_val}_{month_val}.parquet"

            if os.path.exists(local_output_path):
                shutil.rmtree(local_output_path)

            df_filtered = df.filter((col("year") == year_val) & (col("month") == month_val))
            df_filtered.write.mode("overwrite").parquet(local_output_path)

            parquet_files.append({
                "year": year_val,
                "month": month_val,
                "local_path": local_output_path
            })
        
        print(f"Local parquet saved: {local_output_path}")
    
        spark.stop()
        
        gcs_hook = GCSHook(gcp_conn_id)
        gcs_hook.test_connection()
        print("GCS connection test successful!")
        uploaded_files = []
        
        for file_info in parquet_files:
            year_val = file_info["year"]
            month_val = file_info["month"]
            local_dir_path = file_info["local_path"]
            if not os.path.isdir(local_dir_path):
                continue

            part_files = pathlib.Path(local_dir_path).glob("*.parquet")
            for part_file in part_files:
                file_name = f"race_result_{year_val}_{month_val}_{part_file.name}"
                remote_path = f"{base_destination_path}/parquet/{year_val}/{file_name}"

                gcs_hook.upload(
                    bucket_name=destination_bucket,
                    object_name=remote_path,
                    filename=str(part_file)
                )

                uploaded_files.append(remote_path)
    
        for file_info in parquet_files:
            local_path = file_info["local_path"]
            if os.path.exists(local_path):
                shutil.rmtree(local_path)
        
        return(f"Uploaded {len(uploaded_files)} files to GCS.")
    except Exception as e:
        print(f"Error in save_to_gcs: {e}")

default_args = {
    'owner': 'ricky_dezoomcamp_2220',
    'depends_on_past': False,
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

dag = DAG(
    'f1_csv_to_parquet_pyspark_3',
    default_args=default_args,
    description='Convert F1 race results from CSV to Parquet using pyspark and upload to GCS',
    schedule_interval=timedelta(days=1),
    start_date=datetime(2024, 1, 1), # Adjust as needed
    catchup=False,
)

start_task = EmptyOperator(
        task_id='start'
)


load_parquet_to_gcs_task = PythonOperator(
    task_id='fun_load_parquet_to_gcs',
    python_callable=load_parquet_to_gcs,
    op_kwargs={
        'parquet_file_path': '/opt/airflow/dags/temp_parquet'
    },
    provide_context=True,
    dag=dag,
)


end_task = EmptyOperator(
        task_id='end'
)

start_task >> load_parquet_to_gcs_task >> end_task