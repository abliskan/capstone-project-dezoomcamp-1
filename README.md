# capstone-project-dezoomcamp-1-Formula-1-Data Pipeline-for-Race-Analytics
 
## 1. Introduction
Formula 1 Racing Team Alpha seeks to establish a comprehensive data pipeline to transform raw race data into actionable insights that improve race strategy, car performance, and driver development. Currently, the team struggles with siloed data systems, manual data processing, and delayed access to critical information during race weekends. Decision-making is often based on incomplete information or intuition rather than data-driven analysis.
 
## 2. Business Challenges
- Fragmented Data Sources:
 	- competitor performance
 	- historical statistics exist in separate systems with inconsistent formats
 
- Performance Analysis:
 	- Analysts spend excessive time preparing data for analysis rather than deriving insights that could improve car setup and performance.
 
- Driver Development: 
 	- Limited ability to analyze driver performance across multiple dimensions against historical benchmarks and competitors.
 
## 3. Objective
This project aims to build an end-to-end data engineering pipeline that ingests, processes, and analyzes Formula 1 racing data. The data coming from open source on API that handle historical record of race, driver, circuits, and many more data related to Formula 1. The pipeline will extract historical F1 data, transform it into a structured format, and store it in a cloud-based data warehouse. The data will be used for performance analytics, race predictions, and interactive visualizations.
 
## 4. Architecture
![System architecture](https://github.com/abliskan/capstone-project-dezoomcamp-1/blob/main/assets/Final-project-dataflow-v1.png)
 
## 5. Data source
- See the [Dataset link](https://ergast.com/mrd/)
<br>
- There are 7 core files of 26 in total dataset:
 	- driver profile
 	- driver standing
 	- constructor/team profile
 	- constructor/team standing
 	- circuit information
 	- race result 
 	- pitstop
- The data is collected since season 2020 until season 2024
 
## 6. Tools use
- Insfrastructure as Code(IaC): terraform
- Cloud provider: Google Cloud Platform (Free Tier)
- Programming lang: Python (3.12+)
- Containerization: Docker
- Orchestrator: Apache airflow
- Data lake: Google Cloud Storage (standard)
- Data warehouse: Google Bigquery
- Data mart: Google Bigquery
- Transformation: dbt, apache spark
- Data Visualization: Google Looker Studio
 
## 7. Setup guide
### GCP
- Setup new project on google cloud platform:
   - Navigate to the new project.
   - Open the navigation menu and go to “IAM & Admin” > service accounts > create service account
- Download service-account-keys (.json) to local computer
- Move the (.json) file to the project path > credentials
- Change the (.json) file to gcp_credentials.json

### Terraform
Check the detail on this [Link](https://github.com/abliskan/capstone-project-dezoomcamp-1/tree/main/terraform)

### Airflow
Check the detail on this [Link](https://github.com/abliskan/capstone-project-dezoomcamp-1/tree/main/scripts)
<br>
- Data extraction on airflow:
  - task1: dag1-ingest-race-result.py
  - task2: dag2-ingest-pitstop.py
  - task3: dag3-ingest-driver-n-perform.py
  - task4: dag4-ingest-constructor-n-perform.py
  - task5: dag5-ingest-circuits.py
 
- Data convert from .csv format into .parquet format
  - task1: dag1-partition-race-result.py
  - task2: dag2-partition-race_schedule.py

### Bigquery
> On phase-3, all the table inside bigquery dataset (data warehouse & data mart) are relies on an external table from the result of partitioned data using SQL Bigquery.
<br>
>>> External Table <br>
Sample SQL bigquery code

```
# 2020 | race_result
CREATE OR REPLACE EXTERNAL TABLE `<bigquery_project_id>.<bigquery-dataset>.race_result_2020_ext`
OPTIONS (
  format = 'PARQUET',
  uris = ['gs://<gcp_project_id>-<bucket_name>/f1_data/parquet/2020/race_result_*.parquet']
);

# 2020 | driver
CREATE OR REPLACE EXTERNAL TABLE `<bigquery_project_id>.<bigquery-dataset>.driver_2020_ext`
OPTIONS (
  format = 'CSV',
  uris = ['gs://<gcp_project_id>-<bucket_name>/f1_data/driver_2020.csv']
);

# 2020 | constructors
CREATE OR REPLACE EXTERNAL TABLE `<bigquery_project_id>.<bigquery-dataset>.constructors_2020_ext`
OPTIONS (
  format = 'CSV',
  uris = ['gs://<gcp_project_id>-<bucket_name>/f1_data/constructors_2020.csv']
);

# 2020 | Circuits
CREATE OR REPLACE EXTERNAL TABLE `<bigquery_project_id>.<bigquery-dataset>.circuits_2020_ext`
OPTIONS (
  format = 'CSV',
  uris = ['gs://<gcp_project_id>-<bucket_name>/f1_data/circuits_2020.csv']
);

# 2020 | Driver Performance
CREATE OR REPLACE EXTERNAL TABLE `<bigquery_project_id>.<bigquery-dataset>.driver_performance_2020_ext`
OPTIONS (
  format = 'CSV',
  uris = ['gs://<gcp_project_id>-<bucket_name>/f1_data/driver_performance_2020.csv']
);

# 2020 | Constructor Performance
CREATE OR REPLACE EXTERNAL TABLE `<bigquery_project_id>.<bigquery-dataset>.constructor_performance_2020_ext`
OPTIONS (
  format = 'CSV',
  uris = ['gs://<gcp_project_id>-<bucket_name>/f1_data/constructor_perform_2020.csv']
);

# 2020 | Pitstop
CREATE OR REPLACE EXTERNAL TABLE `<bigquery_project_id>.<bigquery-dataset>.pitstop_2020_ext`
OPTIONS (
  format = 'CSV',
  uris = ['gs://<gcp_project_id>-<bucket_name>/f1_data/pitstop_2020.csv']
);
```
<br>
- Staging table inside Bigquery

![alt text](https://github.com/abliskan/capstone-project-dezoomcamp-1/blob/main/assets/bigquery-partition-view-sample.png)
- Dim and fact table inside Bigquery

![alt text](https://github.com/abliskan/capstone-project-dezoomcamp-1/blob/main/assets/bigquery-partition-view-sample.png)
- Mart table

![alt text](https://github.com/abliskan/capstone-project-dezoomcamp-1/blob/main/assets/bigquery-mart-table.png)

### DBT
There are 3 different transformation layer in this process:
- [`Staging`](https://github.com/abliskan/capstone-project-dezoomcamp-1/tree/main/dbt_f1_analytics/models/staging) - read table from bigquery external table, transform the data, and create the result into view stg_* (stg_pitstop, stg_race_result, stg_drivers, stg_driver_performance, stg_constructors, stg_constructors_performance, stg_circuits), example image (stg-driver)
![alt text](https://github.com/abliskan/capstone-project-dezoomcamp-1/blob/main/assets/dbt-dag-stg-driver.PNG)

- [`Data warehouse`](https://github.com/abliskan/capstone-project-dezoomcamp-1/tree/main/dbt_f1_analytics/models/mart/core) - read table from stg_* table, modeling data into data warehouse, and create the result into dim_* table (dim_pitstop, dim_driver, dim_constuctor, dim_race_result)
![alt text](https://github.com/abliskan/capstone-project-dezoomcamp-1/blob/main/assets/dbt-dag-dim-fact-dwh.png)

- [`Data mart`](https://github.com/abliskan/capstone-project-dezoomcamp-1/tree/main/dbt_f1_analytics/models/mart/driver) - (example = driver) read table from dim/fact table, aggregate using sql, and create the result

Check the detail on this [Link](https://github.com/abliskan/capstone-project-dezoomcamp-1/tree/main/dbt_f1_analytics)

### Looker Studio
