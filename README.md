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
- Data extraction on airflow:
  - task1: dag1-ingest-race-result.py
  - task2: dag2-ingest-pitstop.py
  - task3: dag3-ingest-driver-n-perform.py
  - task4: dag4-ingest-constructor-n-perform.py
  - task5: dag5-ingest-circuits.py
  - task6: dag1-partition-race-result.py
  - task7: dag2-partition-race_schedule.py
Check the detail on this [Link](https://github.com/abliskan/capstone-project-dezoomcamp-1/tree/main/scripts)

### Bigquery
Check the detail on this 

### DBT
Check the detail on this [Link](https://github.com/abliskan/capstone-project-dezoomcamp-1/tree/main/dbt_f1_analytics)

### Looker Studio
