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

def fetch_f1_race_result_data(season, json_file_path, **kwargs):
    """
    Fetch all round numbers & race result for a given season.
    """
    base_url = f"http://ergast.com/api/f1/{season}.json"
    try:
        response = requests.get(base_url)
        response.raise_for_status()
        data = response.json()
        races_round = [race["round"] for race in data["MRData"]["RaceTable"]["Races"]]
    except requests.exceptions.RequestException as e:
        print(f"Error fetching F1 rounds for season {season}: {e}")
        return []
    
    api_results = []
    
    try:
        for round_number in races_round:
            race_per_round_url = f"http://ergast.com/api/f1/{season}/{round_number}/results.json"
            response = requests.get(race_per_round_url)
            response.raise_for_status()
            if response.status_code == 200:    
                race_data = response.json()
                races = race_data.get("MRData", {}).get("RaceTable", {}).get("Races", [])
                
                for race in races:
                    race_date = race.get("date", "N/A")
                    race_name = race.get("raceName", "N/A")
                        
                    for result in race.get("Results", []):
                        driver = result.get("Driver", {})
                        constructor = result.get("Constructor", {})
                        time = result.get("Time", {})
                        fastest_lap = result.get("FastestLap", {})
                        
                        api_results.append({
                            "driverId": driver.get("driverId", "N/A"),
                            "season": season,
                            "round": round_number,
                            "raceName": race_name,
                            "date": race_date,
                            "driverName": f"{driver.get('givenName', 'N/A')} {driver.get('familyName', 'N/A')}",
                            "constructorId": constructor.get("constructorId", "N/A"),
                            "constructorName": constructor.get("name", "N/A"),
                            "grid": result.get("grid", "N/A"),
                            "position": result.get("position", "N/A"),
                            "points": result.get("points", "N/A"),
                            "status": result.get("status", "N/A"),
                            "laps": result.get("laps", "N/A"),
                            "time": time.get("time", "N/A"),
                            "fastest_rank": fastest_lap.get("rank", "N/A"),
                            "fastest_lap": fastest_lap.get("lap", "N/A"),
                            "fastest_time": fastest_lap.get("Time", {}).get("time", "N/A"),
                            "fastest_speed": fastest_lap.get("AverageSpeed", {}).get("speed", "N/A"),
                        })    
            else:
                print(f"Failed to fetch data for round {round_number} in season.")
                break
        
        with open(json_file_path, "w") as f:
            json.dump(api_results, f, indent=2)
    except requests.exceptions.RequestException as e:
        print(f"Error fetching race result on round for season {season}: {e}")
        return []   

def convert_json_to_csv(json_file_path, csv_file_path, **kwargs):
    """
    Convert JSON F1 JSON data to CSV format.
    """
    with open(json_file_path, 'r') as f:
        race_result_data = json.load(f)

    if isinstance(race_result_data, dict):  
        f1_race_dict = [race_result_data]
    else:
        print("Invalid data format")
        return None

    race_df = pd.DataFrame(f1_race_dict)
    race_df.insert(0, "raceResultId", [f"{i+1}" for i in range(len(race_df))])
    try:
        with open(csv_file_path, "w") as f:
            race_df.to_csv(f, index=False)
    except requests.exceptions.RequestException as e:
        print(f"Error converting JSON to CSV: {e}")
    
def upload_to_gcs(season, csv_file_path, **kwargs):
    """
    Save F1 data to GCS.
    """
    try: 
        bucket_name = kwargs.get("bucket_name", GCS_BUCKET_NAME)
        gcp_conn_id = kwargs.get("gcp_conn_id", GCP_CONN_ID)
        object_name = f"race_result_{season}.csv"
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

        return f"Data saved to gs://{bucket_name}/{destination_blob_name}"
    except Exception as e:
        print(f"Error in save_to_gcs: {e}")

default_args = {
    'owner': 'ricky_dezoomcamp',
    'depends_on_past': False,
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

dag = DAG(
    'f1_data_pipeline',
    default_args=default_args,
    description='Extract F1 data from Ergast API and store in GCS',
    schedule_interval=timedelta(days=1),
    start_date=datetime(2024, 1, 1), # Adjust as needed
    catchup=False,
)

start_task = EmptyOperator(
        task_id='start'
)


fetch_f1_race_results_data_task = PythonOperator(
    task_id="fun_fetch_f1_race_results",
    python_callable=fetch_f1_race_result_data,
    op_kwargs={
        'season': 2024, # Adjust as needed (2020, 2021, 2022, 2023, 2024)
        'json_file_path': '/opt/airflow/dags/race_result_2024.json' # Adjust as needed (2020, 2021, 2022, 2023, 2024)
    },
    provide_context=True,
    dag=dag,
)

convert_json_to_csv_task = PythonOperator(
    task_id='fun_convert_json_to_csv',
    python_callable=convert_json_to_csv,
    op_kwargs={
        'json_file_path': '/opt/airflow/dags/race_result_2024.json', # Adjust as needed (2020, 2021, 2022, 2023, 2024)
        'csv_file_path': '/opt/airflow/dags/race_result_2024.csv' # Adjust as needed (2020, 2021, 2022, 2023, 2024)
    },
    provide_context=True,
    dag=dag,
)

load_to_gcs_task = PythonOperator(
    task_id='fun_load_to_gcs',
    python_callable=upload_to_gcs,
    op_kwargs={
        'season': 2024, # Adjust as needed (2020, 2021, 2022, 2023, 2024)
        'csv_file_path': '/opt/airflow/dags/race_result_2024.csv' # Adjust as needed (2020, 2021, 2022, 2023, 2024)
    },
    provide_context=True,
    dag=dag,
)


end_task = EmptyOperator(
        task_id='end'
)

start_task >> fetch_f1_race_results_data_task >> convert_json_to_csv_task >> load_to_gcs_task >> end_task