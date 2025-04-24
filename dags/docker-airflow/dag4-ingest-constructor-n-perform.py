from airflow import DAG
from airflow.operators.empty import EmptyOperator
from airflow.operators.python import PythonOperator
from airflow.providers.google.cloud.hooks.gcs import GCSHook

import os
import json
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

def fetch_f1_constructor(season, constructor_json_file_path, **kwargs):
    """
    Fetch all F1 constructor for a given season and generate constructorKeyId.
    """
    constructors_url = f"http://ergast.com/api/f1/{season}/constructors.json"
    try:
        response = requests.get(constructors_url)
        response.raise_for_status()

        if response.status_code == 200:
            constructors_data = response.json()
            constructors = constructors_data['MRData']['ConstructorTable']['Constructors']
        
            constructor_list = [{
                "season": season,
                "constructorId": constructor["constructorId"],
                "constructorName": constructor["name"],
                "nationality": constructor["nationality"]
            } for constructor in constructors]
        else:
            print(f"Failed to fetch drivers for {season}: {response.status_code}")
            return []
        
        if constructor_list:
            with open(constructor_json_file_path, 'w') as f:
                json.dump(constructor_list, f, indent=4)
        else:
            print(f"No constructor data found for season {season}.")
    except requests.exceptions.RequestException as e:
        print(f"Error fetching data for season {season}: {e}")
        return []
    
def fetch_f1_constructor_perform(season, constructor_perform_json_file_path, **kwargs):
    """
    Fecth All F1 constructore performance for a given season and generate constructorPerfKeyId.
    """
    constructor_standing_url = f"http://ergast.com/api/f1/{season}/constructorStandings.json"
    api_result_constructor = []
    try:
        response = requests.get(constructor_standing_url)
        response.raise_for_status()
        
        if response.status_code == 200:
            constructor_standing_data = response.json()
            standings = constructor_standing_data['MRData']['StandingsTable']['StandingsLists']
            for constructor in standings[0].get("ConstructorStandings", []):
                    api_result_constructor.append({
                        "season": season,
                        "constructorId": constructor['Constructor']['constructorId'],
                        "constructorName": constructor['Constructor'].get('name'),
                        "position": constructor.get("position"),
                        "points": constructor.get("points"),
                        "wins": constructor.get("wins"),
                        "nationality": constructor['Constructor'].get("nationality"),
                        "url": constructor['Constructor'].get("url")
                    })
        else:
            print(f"Failed to fetch constructor performance for {season}")
        
        if api_result_constructor:
            with open(constructor_perform_json_file_path, 'w') as f:
                json.dump(api_result_constructor, f, indent=4)
        else:
            print(f"No constructor data found for season {season}.")
    except requests.exceptions.RequestException as e:
        print(f"Error fetching data for season {season}: {e}")
        return []

def convert_json_constructor_to_csv(constructor_json_file_path, constructor_csv_file_path, **kwargs):
    """
    Convert JSON constructor data to CSV and save locally.
    """
    with open(constructor_json_file_path, 'r') as f:
        constructor_data = json.load(f)
    
    if isinstance(constructor_data, dict):
        f1_constructor_dict = [constructor_data]
    else:
        print("Invalid data format")
        return None
    
    f1_constructor_df = pd.DataFrame(f1_constructor_dict)
    f1_constructor_df.insert(0, "constructorKeyId", [f"{i+1}" for i in range(len(f1_constructor_df))])
    try:
        with open(constructor_csv_file_path, 'w') as file:
            f1_constructor_df.to_csv(file, index=False)
    except requests.exceptions.RequestException as e:
        print(f"Error converting JSON to CSV: {e}")

def convert_json_constructor_perform_to_csv(constructor_perform_json_file_path, constructor_perform_csv_file_path, **kwargs):
    """
    Convert JSON driver performance data to CSV and save locally.
    """
    with open(constructor_perform_json_file_path, 'r') as f:
        constructor_perform_data = json.load(f)
    
    if isinstance(constructor_perform_data, dict):
        f1_constructor_perform_dict = [constructor_perform_data]
    else:
        print("Invalid data format")
        return None
    
    f1_constructor_perform_df = pd.DataFrame(f1_constructor_perform_dict)
    f1_constructor_perform_df.insert(0, "constructorPerfKeyId", [f"{i+1}" for i in range(len(f1_constructor_perform_df))])
    try:
        with open(constructor_perform_csv_file_path, 'w') as file:
            f1_constructor_perform_df.to_csv(file, index=False)
    except requests.exceptions.RequestException as e:
        print(f"Error converting JSON to CSV: {e}")
    
def upload_constructor_data_to_gcs(season, constructor_csv_file_path, **kwargs):
    """
    Upload Driver CSV file to Google Cloud Storage.
    """
    bucket_name = kwargs.get("bucket_name", GCS_BUCKET_NAME)
    gcp_conn_id = kwargs.get("gcp_conn_id", GCP_CONN_ID)
    object_name = f"constructors_{season}.csv"
    mime_type = kwargs.get("mime_type", "text/csv")
    
    if not bucket_name:
        raise ValueError("GCS Bucket name is missing!")
    if not gcp_conn_id:
        raise ValueError("GCP Connection ID is missing!")
    if not object_name:
        raise ValueError("GCP object name is missing!")
        
    gcs_hook = GCSHook(gcp_conn_id=gcp_conn_id)
    destination_blob_name = f"f1_data/{object_name}"
    with open(constructor_csv_file_path, 'rb') as file_obj:
        gcs_hook.upload(
            bucket_name=bucket_name,
            object_name=destination_blob_name,
            data=file_obj.read(),
            mime_type=mime_type
        )

def upload_constructor_perform_data_to_gcs(season, constructor_perform_csv_file_path, **kwargs):
    """
    Upload Driver CSV file to Google Cloud Storage.
    """
    bucket_name = kwargs.get("bucket_name", GCS_BUCKET_NAME)
    gcp_conn_id = kwargs.get("gcp_conn_id", GCP_CONN_ID)
    object_name = f"constructor_perform_{season}.csv"
    mime_type = kwargs.get("mime_type", "text/csv")
    
    if not bucket_name:
        raise ValueError("GCS Bucket name is missing!")
    if not gcp_conn_id:
        raise ValueError("GCP Connection ID is missing!")
    if not object_name:
        raise ValueError("GCP object name is missing!")
        
    gcs_hook = GCSHook(gcp_conn_id=gcp_conn_id)
    destination_blob_name = f"f1_data/{object_name}"
    with open(constructor_perform_csv_file_path, 'rb') as file_obj:
        gcs_hook.upload(
            bucket_name=bucket_name,
            object_name=destination_blob_name,
            data=file_obj.read(),
            mime_type=mime_type
        )

default_args = {
    "owner": "ricky_dezoomcamp_1433",
    'depends_on_past': False,
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}



# Define DAG
dag = DAG(
    dag_id="f1_data_pipeline_3",
    default_args=default_args,
    description='Extract F1 data from Ergast API and store in GCS',
    schedule_interval=timedelta(days=1),
    start_date=datetime(2024, 1, 1), # Adjust as needed
    catchup=False,
)

start_task = EmptyOperator(
        task_id='start'
)


fetch_f1_constructor_data_task = PythonOperator(
    task_id="fun_fetch_f1_constructor",
    python_callable=fetch_f1_constructor,
    op_kwargs={
        'season': 2024, # Adjust as needed (2020, 2021, 2022, 2023, 2024)
        'constructor_json_file_path': '/opt/airflow/dags/constructor_2024.json', # Adjust as needed (2020, 2021, 2022, 2023, 2024)
    },
    provide_context=True,
    dag=dag,
)

fetch_f1_constructor_perform_data_task = PythonOperator(
    task_id="fun_fetch_f1_constructor",
    python_callable=fetch_f1_constructor_perform,
    op_kwargs={
        'season': 2024, # Adjust as needed (2020, 2021, 2022, 2023, 2024)
        'constructor_perform_json_file_path': '/opt/airflow/dags/constructor_perform_2024.json', # Adjust as needed (2020, 2021, 2022, 2023, 2024)
    },
    provide_context=True,
    dag=dag,
)

convert_json_constructor_to_csv_task = PythonOperator(
    task_id='fun_convert_json_constructor_to_csv',
    python_callable=convert_json_constructor_to_csv,
    op_kwargs={
        'constructor_json_file_path': '/opt/airflow/dags/constructor_2024.json', # Adjust as needed (2020, 2021, 2022, 2023, 2024)
        'constructor_csv_file_path': '/opt/airflow/dags/constructor_2024.csv' # Adjust as needed (2020, 2021, 2022, 2023, 2024)
    },
    provide_context=True,
    dag=dag,
)

convert_json_constructor_perform_to_csv_task = PythonOperator(
    task_id='fun_convert_json_constructor_perform_to_csv',
    python_callable=convert_json_constructor_perform_to_csv,
    op_kwargs={
        'constructor_perform_json_file_path': '/opt/airflow/dags/constructor_perform_2024.json', # Adjust as needed (2020, 2021, 2022, 2023, 2024)
        'constructor_perform_csv_file_path': '/opt/airflow/dags/constructor_perform_2024.csv' # Adjust as needed (2020, 2021, 2022, 2023, 2024)
    },
    provide_context=True,
    dag=dag,
)

load_constructor_data_to_gcs_task = PythonOperator(
    task_id='fun_load_constructor_data_to_gcs',
    python_callable=upload_constructor_data_to_gcs,
    op_kwargs={
        'season': 2024, # Adjust as needed (2020, 2021, 2022, 2023, 2024)
        'constructor_csv_file_path': '/opt/airflow/dags/constructor_2024.csv' # Adjust as needed (2020, 2021, 2022, 2023, 2024)
    },
    provide_context=True,
    dag=dag,
)


load_constructor_perform_data_to_gcs_task = PythonOperator(
    task_id='fun_load_constructor_perform_data_to_gcs',
    python_callable=upload_constructor_perform_data_to_gcs,
    op_kwargs={
        'season': 2024, # Adjust as needed (2020, 2021, 2022, 2023, 2024)
        'constructor_perform_csv_file_path': '/opt/airflow/dags/constructor_perform_2024.csv' # Adjust as needed (2020, 2021, 2022, 2023, 2024)
    },
    provide_context=True,
    dag=dag,
)


end_task = EmptyOperator(
        task_id='end'
)

start_task >> fetch_f1_constructor_data_task >> convert_json_constructor_to_csv_task >> load_constructor_data_to_gcs_task >> end_task
start_task >> fetch_f1_constructor_perform_data_task >> convert_json_constructor_perform_to_csv_task >> load_constructor_perform_data_to_gcs_task >> end_task