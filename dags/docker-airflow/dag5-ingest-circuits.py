from airflow import DAG
from airflow.operators.empty import EmptyOperator
from airflow.operators.python import PythonOperator
from airflow.providers.google.cloud.hooks.gcs import GCSHook

import os
import json
# import time
import pandas as pd
import requests
from pandas import DataFrame
from datetime import datetime, timedelta
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

GCS_BUCKET_NAME = os.getenv('GCS_BUCKET_NAME')
GCP_CONN_ID = os.getenv('GCP_CONN_ID')
RATE_LIMIT_DELAY = float(os.getenv("RATE_LIMIT_DELAY", 1))  # Default 1 second delay

def fetch_f1_circuits(season, json_file_path, **kwargs):
    """
    Fetch F1 circuits for a given season and error handling.
    """
    circuit_url = f"http://ergast.com/api/f1/{season}/circuits.json"
    circuit_list = []
    try:
        response = requests.get(circuit_url)
        response.raise_for_status()
        
        if response.status_code == 200:
            circuit_data = response.json()
            circuits = circuit_data["MRData"]["CircuitTable"]["Circuits"]
            for circuit in circuits:
                circuit_list.extend({
                    "circuitId": circuit.get("circuitId", "N/A"),
                    "circuitName": circuit.get("circuitName", "N/A"),
                    "country": circuit.get("Location", {}).get("country", "N/A"),
                    "locality": circuit.get("Location", {}).get("locality", "N/A"),
                    "lat": circuit.get("Location", {}).get("lat", "N/A"),
                    "long": circuit.get("Location", {}).get("long", "N/A"),
                    }
                )
        else:
            print(f"Failed to fetch data from {circuit_url}: {response.status_code}")
            
        if circuit_list:
            with open(json_file_path, 'w') as f:
                json.dump(circuit_list, f, indent=4)
        else:
            print(f"No circuit data found for reason.")
    except requests.exceptions.RequestException as e:
        print(f"Error fetching circuits for season {season}: {e}")
        return []

def convert_json_to_csv(json_file_path, csv_file_path, **kwargs):
    """
    Convert JSON data to CSV and save locally.
    """
    with open(json_file_path, 'r') as f:
        circuit_data = json.load(f)
    
    if isinstance(circuit_data, dict):
        circuit_dict = [circuit_data]
    else:
        print("Invalid data format")
        return None
    
    circuit_df = pd.DataFrame(circuit_dict)
    circuit_df.insert(0, "circuitKeyId", [f"{i+1}" for i in range(len(circuit_df))])
    try:
        with open(csv_file_path, 'w') as file:
            circuit_df.to_csv(file, index=False)
    except requests.exceptions.RequestException as e:
        print(f"Error converting JSON to CSV: {e}")

def upload_to_gcs(season, csv_file_path, **kwargs):
    """
    Upload CSV file to Google Cloud Storage.
    """
    bucket_name = kwargs.get("bucket_name", GCS_BUCKET_NAME)
    gcp_conn_id = kwargs.get("gcp_conn_id", GCP_CONN_ID)
    object_name = f"circuits_{season}.csv"
    mime_type = kwargs.get("mime_type", "text/csv")
    
    if not bucket_name:
        raise ValueError("GCS Bucket name is missing!")
    if not gcp_conn_id:
        raise ValueError("GCP Connection ID is missing!")
    if not object_name:
        raise ValueError("GCP object name is missing!")
        
    gcs_hook = GCSHook(gcp_conn_id=gcp_conn_id)
    destination_blob_name = f"f1_data/{object_name}"
    with open(csv_file_path, 'rb') as file_obj:
        gcs_hook.upload(
            bucket_name=bucket_name,
            object_name=destination_blob_name,
            data=file_obj.read(),
            mime_type=mime_type
        )

default_args = {
    "owner": "ricky_dezoomcamp_1580",
    'depends_on_past': False,
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}



# Define DAG
dag = DAG(
    dag_id="f1_data_pipeline_4",
    default_args=default_args,
    description='Extract F1 data from Ergast API and store in GCS',
    schedule_interval=timedelta(days=1),
    start_date=datetime(2024, 1, 1), # Adjust as needed
    catchup=False,
)

start_task = EmptyOperator(
        task_id='start'
)


fetch_f1_circuits_data_task = PythonOperator(
    task_id="fun_fetch_f1_circuits",
    python_callable=fetch_f1_circuits,
    op_kwargs={
        'season': 2024, # Adjust as needed (2020, 2021, 2022, 2023, 2024)
        'json_file_path': '/opt/airflow/dags/circuits_2024.json' # Adjust as needed (2020, 2021, 2022, 2023, 2024)
    },
    provide_context=True,
    dag=dag,
)

convert_json_to_csv_task = PythonOperator(
    task_id='fun_convert_json_to_csv',
    python_callable=convert_json_to_csv,
    op_kwargs={
        'json_file_path': '/opt/airflow/dags/circuits_2024.json', # Adjust as needed (2020, 2021, 2022, 2023, 2024)
        'csv_file_path': '/opt/airflow/dags/circuits_2024.csv' # Adjust as needed (2020, 2021, 2022, 2023, 2024)
    },
    provide_context=True,
    dag=dag,
)

load_to_gcs_task = PythonOperator(
    task_id='fun_load_to_gcs',
    python_callable=upload_to_gcs,
    op_kwargs={
        'season': 2024, # Adjust as needed (2020, 2021, 2022, 2023, 2024)
        'csv_file_path': '/opt/airflow/dags/circuits_2024.csv' # Adjust as needed (2020, 2021, 2022, 2023, 2024)
    },
    provide_context=True,
    dag=dag,
)


end_task = EmptyOperator(
        task_id='end'
)

start_task >> fetch_f1_circuits_data_task >> convert_json_to_csv_task >> load_to_gcs_task >> end_task