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

def fetch_f1_drivers(season, drivers_json_file_path, **kwargs):
    """
    Fetch all F1 drivers for a given season and generate driverKeyId.
    """
    driver_url = f"http://ergast.com/api/f1/{season}/drivers.json"
    try:
        response = requests.get(driver_url)
        response.raise_for_status()

        if response.status_code == 200:
            data = response.json()
            drivers = data["MRData"]["DriverTable"]["Drivers"]
            driver_list = [{
            "season": season,
            "driverId": driver["driverId"],
            "driverName": f"{driver['givenName']} {driver['familyName']}",
            "dateOfBirth(dob)": driver["dateOfBirth"],
            "nationality": driver["nationality"]
        } for driver in drivers]
        else:
            print(f"Failed to fetch drivers for {season}: {response.status_code}")
            return []
        
        if driver_list:
            with open(drivers_json_file_path, 'w') as f:
                json.dump(driver_list, f, indent=4)
        else:
            print(f"No driver data found for reason.")
    except requests.exceptions.RequestException as e:
        print(f"Error fetching data for season {season}: {e}")
        return []

def fetch_f1_drivers_perform(season, drivers_perform_json_file_path, **kwargs):
    """
    Fetch all F1 drivers performance for a given season and generate driverPerfKeyId.
    """
    driver_standing_url = f"http://ergast.com/api/f1/{season}/driverStandings.json"
    api_results = []
    try:
        response = requests.get(driver_standing_url)
        response.raise_for_status()
        
        if response.status_code == 200:
            driver_standing_data = response.json()
            standings = driver_standing_data["MRData"]["StandingsTable"]["StandingsLists"]
            for standing in standings:
                for driver_standing in standing.get("DriverStandings", []):
                    driver = driver_standing.get("Driver", {})
                    constructor = driver_standing.get("Constructors", [{}])[0]  # Get the first constructor
                
                    api_results.append({
                        "season": season,
                        "driverId": driver.get("driverId", "N/A"),
                        "driverName": f"{driver.get('givenName', 'N/A')} {driver.get('familyName', 'N/A')}",
                        "constructorId": constructor.get("constructorId", "N/A"),
                        "constructorName": constructor.get("name", "N/A"),
                        "position": int(driver_standing.get("position", 0)),
                        "points": float(driver_standing.get("points", 0)),
                        "wins": int(driver_standing.get("wins", 0))
                    })
        else:
            print(f"Failed to fetch drivers for {season}: {response.status_code}")
            return []
        
        if api_results:
            with open(drivers_perform_json_file_path, 'w') as f:
                json.dump(api_results, f, indent=4)
        else:
            print(f"No driver data found for reason.")
    except requests.exceptions.RequestException as e:
        print(f"Error fetching data for season {season}: {e}")
        return []

def convert_json_driver_to_csv(drivers_json_file_path, driver_csv_file_path, **kwargs):
    """
    Convert JSON driver data to CSV and save locally.
    """
    with open(drivers_json_file_path, 'r') as f:
        driver_data = json.load(f)

    if isinstance(driver_data, dict):
        f1_driver_dict = [driver_data]
    else:
        print("Invalid data format")
        return None
     
    f1_driver_df = pd.DataFrame(f1_driver_dict)
    f1_driver_df.insert(0, "pitstopId", [f"{i+1}" for i in range(len(f1_driver_df))])
    try:
        with open(driver_csv_file_path, 'w') as file:
            f1_driver_df.to_csv(file, index=False)
    except requests.exceptions.RequestException as e:
        print(f"Error converting JSON to CSV: {e}")

def convert_json_driver_perform_to_csv(drivers_perform_json_file_path, driver_perform_csv_file_path, **kwargs):
    """
    Convert JSON driver performance data to CSV and save locally.
    """
    with open(drivers_perform_json_file_path, 'r') as f:
        driver_perform_data = json.load(f)
    
    if isinstance(driver_perform_data, dict):
        f1_driver_perform_dict = [driver_perform_data]
    else:
        print("Invalid data format")
        return None
    
    f1_driver_perform_df = pd.DataFrame(f1_driver_perform_dict)
    f1_driver_perform_df.insert(0, "pitstopId", [f"{i+1}" for i in range(len(f1_driver_perform_df))])
    
    try:
        with open(driver_perform_csv_file_path, 'w') as file:
            f1_driver_perform_df.to_csv(file, index=False)
    except requests.exceptions.RequestException as e:
        print(f"Error converting JSON to CSV: {e}")

def upload_driver_data_to_gcs(season, driver_csv_file_path, **kwargs):
    """
    Upload Driver CSV file to Google Cloud Storage.
    """
    bucket_name = kwargs.get("bucket_name", GCS_BUCKET_NAME)
    gcp_conn_id = kwargs.get("gcp_conn_id", GCP_CONN_ID)
    object_name = f"driver_{season}.csv"
    mime_type = kwargs.get("mime_type", "text/csv")
    
    if not bucket_name:
        raise ValueError("GCS Bucket name is missing!")
    if not gcp_conn_id:
        raise ValueError("GCP Connection ID is missing!")
    if not object_name:
        raise ValueError("GCP object name is missing!")
        
    gcs_hook = GCSHook(gcp_conn_id=gcp_conn_id)
    destination_blob_name = f"f1_data/{object_name}"
    with open(driver_csv_file_path, 'rb') as file_obj:
        gcs_hook.upload(
            bucket_name=bucket_name,
            object_name=destination_blob_name,
            data=file_obj.read(),
            mime_type=mime_type
        )
        
def upload_driver_perform_data_to_gcs(season, driver_perform_csv_file_path, **kwargs):
    """
    Upload Driver Perform CSV file to Google Cloud Storage.
    """
    bucket_name = kwargs.get("bucket_name", GCS_BUCKET_NAME)
    gcp_conn_id = kwargs.get("gcp_conn_id", GCP_CONN_ID)
    object_name = f"driver_performance_{season}.csv"
    mime_type = kwargs.get("mime_type", "text/csv")
    
    if not bucket_name:
        raise ValueError("GCS Bucket name is missing!")
    if not gcp_conn_id:
        raise ValueError("GCP Connection ID is missing!")
    if not object_name:
        raise ValueError("GCP object name is missing!")
        
    gcs_hook = GCSHook(gcp_conn_id=gcp_conn_id)
    destination_blob_name = f"f1_data/{object_name}"
    with open(driver_perform_csv_file_path, 'rb') as file_obj:
        gcs_hook.upload(
            bucket_name=bucket_name,
            object_name=destination_blob_name,
            data=file_obj.read(),
            mime_type=mime_type
        )

default_args = {
    "owner": "ricky_dezoomcamp_1102",
    'depends_on_past': False,
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}


dag = DAG(
    dag_id="f1_data_pipeline_2",
    default_args=default_args,
    description='Extract F1 data from Ergast API and store in GCS',
    schedule_interval=timedelta(days=1),
    start_date=datetime(2024, 1, 1), # Adjust as needed
    catchup=False,
)

start_task = EmptyOperator(
        task_id='start'
)


fetch_f1_drivers_data_task = PythonOperator(
    task_id="fun_fetch_f1_driver_data",
    python_callable=fetch_f1_drivers,
    op_kwargs={
        'season': 2024, # Adjust as needed (2020, 2021, 2022, 2023, 2024)
        'drivers_json_file_path': '/opt/airflow/dags/drivers_2024.json', # Adjust as needed (2020, 2021, 2022, 2023, 2024)
    },
    provide_context=True,
    dag=dag,
)

fetch_f1_drivers_perform_data_task = PythonOperator(
    task_id="fun_fetch_f1_driver_perform_data",
    python_callable=fetch_f1_drivers_perform,
    op_kwargs={
        'season': 2024, # Adjust as needed (2020, 2021, 2022, 2023, 2024)
        'drivers_perform_json_file_path': '/opt/airflow/dags/drivers_perform_2024.json', # Adjust as needed (2020, 2021, 2022, 2023, 2024)
    },
    provide_context=True,
    dag=dag,
)

convert_json_driver_to_csv_task = PythonOperator(
    task_id='fun_convert_json_driver_to_csv',
    python_callable=convert_json_driver_to_csv,
    op_kwargs={
        'drivers_json_file_path': '/opt/airflow/dags/drivers_2024.json', # Adjust as needed (2020, 2021, 2022, 2023, 2024)
        'driver_csv_file_path': '/opt/airflow/dags/drivers_2024.csv' # Adjust as needed (2020, 2021, 2022, 2023, 2024)
    },
    provide_context=True,
    dag=dag,
)

convert_json_driver_perform_to_csv_task = PythonOperator(
    task_id='fun_convert_json_driver_perform_to_csv',
    python_callable=convert_json_driver_perform_to_csv,
    op_kwargs={
        'drivers_perform_json_file_path': '/opt/airflow/dags/drivers_perform_2024.json', # Adjust as needed (2020, 2021, 2022, 2023, 2024)
        'drivers_perform_csv_file_path': '/opt/airflow/dags/drivers_perform_2024.csv' # Adjust as needed (2020, 2021, 2022, 2023, 2024)
    },
    provide_context=True,
    dag=dag,
)

upload_driver_data_to_gcs_task = PythonOperator(
    task_id='fun_load_driver_data_to_gcs',
    python_callable=upload_driver_data_to_gcs,
    op_kwargs={
        'season': 2024,
        'driver_csv_file_path': '/opt/airflow/dags/drivers_2024.csv' # Adjust as needed (2020, 2021, 2022, 2023, 2024)
    },
    provide_context=True,
    dag=dag,
)

upload_driver_perform_data_to_gcs_task = PythonOperator(
    task_id='fun_load_data_driver_perform_to_gcs',
    python_callable=upload_driver_perform_data_to_gcs,
    op_kwargs={
        'season': 2024, # Adjust as needed (2020, 2021, 2022, 2023, 2024)
        'driver_perform_csv_file_path': '/opt/airflow/dags/drivers_perform_2024.csv' # Adjust as needed (2020, 2021, 2022, 2023, 2024)
    },
    provide_context=True,
    dag=dag,
)

    
end_task = EmptyOperator(
        task_id='end'
)

start_task >> fetch_f1_drivers_data_task >> convert_json_driver_to_csv_task >> upload_driver_data_to_gcs_task >> end_task
start_task >> fetch_f1_drivers_perform_data_task >> convert_json_driver_perform_to_csv_task >> upload_driver_perform_data_to_gcs_task >> end_task