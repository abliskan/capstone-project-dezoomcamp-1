{{ 
    config(
        materialized='view'
    )
}}

SELECT 
    "2020" AS constructor_year,
    constructorKeyId AS constructor_keyid,
    season,
    constructorId AS constructor_id,
    constructorName AS constructor_name,
    nationality
FROM {{ source('<bigquery_dataset_id_main>', 'constructors_2020_ext') }}
UNION ALL
SELECT 
    "2021" AS constructor_year,
    constructorKeyId AS constructor_keyid,
    season,
    constructorId AS constructor_id,
    constructorName AS constructor_name,
    nationality
FROM {{ source('<bigquery_dataset_id_main>', 'constructors_2021_ext') }}
UNION ALL
SELECT 
    "2022" AS constructor_year,
    constructorKeyId AS constructor_keyid,
    season,
    constructorId AS constructor_id,
    constructorName AS constructor_name,
    nationality
FROM {{ source('<bigquery_dataset_id_main>', 'constructors_2022_ext') }}
UNION ALL
SELECT 
    "2023" AS constructor_year,
    constructorKeyId AS constructor_keyid,
    season,
    constructorId AS constructor_id,
    constructorName AS constructor_name,
    nationality
FROM {{ source('<bigquery_dataset_id_main>', 'constructors_2023_ext') }}
UNION ALL
SELECT 
    "2024" AS constructor_year,
    constructorKeyId AS constructor_keyid,
    season,
    constructorId AS constructor_id,
    constructorName AS constructor_name,
    nationality
FROM {{ source('<bigquery_dataset_id_main>', 'constructors_2024_ext') }}