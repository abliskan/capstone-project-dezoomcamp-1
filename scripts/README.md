# Using apache airflow and python for data ingestion 
## Installation and Setup
> On phase-1, the pipeline will extract batch (@daily) from historical F1 data, convert it from unstructured format (.json) into a structured format (.csv), and store the (.csv) f1 data inside datalake (google cloud storage bucket).

![alt text](https://github.com/abliskan/capstone-project-dezoomcamp-1/blob/main/assets/SS-Extract-all-Graph-airflow.PNG)

1. Navigate to the project directory and activating virtual environment
```
cd .\capstone-project-dezoomcamp-1.\
conda activate <virtual_env_name>
```

2. Pull the docker image
```
docker-compose -f airflow-docker-compose.yaml build
```

3. Starts the containers 
```
docker-compose -f airflow-docker-compose.yaml up
```

4. Get inside the airflow container
```
docker exec -it <airflow-webserver-container-id> bash
```

5. Check the airflow connection, add the GCP_PROJECT_ID and credentials_path if gcp connection wasn't on the airflow connection list
```
airflow connections list
```

note: <br>
- use this command to add connection
```
airflow connections add '<GCP_PROJECT_ID>' \
          --conn-type google_cloud_platform \
          --conn-extra '{"extra__google_cloud_platform__keyfile_dict": "/opt/airflow/<insert_sample_gcp_credentials_path>", "extra__google_cloud_platform__scope": "https://www.googleapis.com/auth/cloud-platform"}'
```

- use this command to delete the connection
```
airflow connections delete <name_conn_id>
```

5a. Access the airflow webserver(airflow UI)
```
open http://localhost:8080 on the browser
```

5b. Type username and password that already been set on airflow-docker-compose.yaml or .env file <br>
5c. Click the DAG name "dag1-ingest-race-result" on DAG waiting list to run the DAG <br>
note: do the same for other dag-ingest-*.py <br>
5d. After all success and finished
```
logout from airflow UI
```

6. Stop and remove the the airflow container
```
docker-compose -f airflow-docker-compose.yaml down
```
<br>
- The DAG orchestrates the python operator for scheduler: <br>
	- ./airflow/dags/: contains airflow DAG that manage ETL process <br>
	- ./airflow/dags/f1-data-csv/: csv file from data source that save on local computer <br>
	- ./airflow/dags/f1-data-json/: json file from data source that save on local computer

## GCS
![alt text](https://github.com/abliskan/capstone-project-dezoomcamp-1/blob/main/assets/GCP-F1-ALL-DATA-2020-2024-1.PNG)
