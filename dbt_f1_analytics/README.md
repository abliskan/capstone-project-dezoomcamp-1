# Using dbt for data transformation and data modeling 
> On phase-4, dbt build data pipelines from bigquery external table for data warehousing and rovides functions like testing and version control that guarantee the consistency and accuracy of the data

![alt text](https://github.com/abliskan/capstone-project-dezoomcamp-1/blob/main/assets/dbt-dag-v1.png)

1. Navigate to the project directory and activating virtual environment
```
cd .\capstone-project-dezoomcamp-1.\
conda activate <virtual_env_name>
```

2. Create a Virtual Environment
```
python -m venv dbt-env
```

3. Activate the Virtual Environment
```
dbt-env\Scripts\activate
```

4. Initializing the dbt Project
```
dbt init
```

5. Verify that your configuration has been set up correctly
```
dbt debug
```

6. Try running the following commands:
```
dbt run
dbt test
```

7. Generate documentation for this model
```
dbt docs generate
```

8. Serve the documentation locally
```
dbt docs serve
```
<br>
ERD for data warehouse data modeling
![alt text](https://github.com/abliskan/capstone-project-dezoomcamp-1/blob/main/assets/DWH-Schema-Design-v1.png)

## Resources:
- Learn more about dbt [in the docs](https://docs.getdbt.com/docs/introduction)
- Check out [Discourse](https://discourse.getdbt.com/) for commonly asked questions and answers
- Join the [chat](https://community.getdbt.com/) on Slack for live discussions and support
- Find [dbt events](https://events.getdbt.com) near you
- Check out [the blog](https://blog.getdbt.com/) for the latest news on dbt's development and best practices
