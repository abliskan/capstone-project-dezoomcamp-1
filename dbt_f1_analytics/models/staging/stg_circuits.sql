{{ 
    config(
        materialized='view'
    )
}}

SELECT 
    "2020" AS constructor_year,
    circuitKeyId AS circuit_keyId,
    season,
    circuitId AS circuit_id,
    circuitName AS circuit_name,
    country,
    locality,
    lat,
    long
FROM {{ source('<bigquery_dataset_id_main>', 'circuits_2020_ext') }}
UNION ALL
SELECT 
    "2021" AS constructor_year,
    circuitKeyId AS circuit_keyId,
    season,
    circuitId AS circuit_id,
    circuitName AS circuit_name,
    country,
    locality,
    lat,
    long
FROM {{ source('<bigquery_dataset_id_main>', 'circuits_2021_ext') }}
UNION ALL
SELECT 
    "2022" AS constructor_year,
    circuitKeyId AS circuit_keyId,
    season,
    circuitId AS circuit_id,
    circuitName AS circuit_name,
    country,
    locality,
    lat,
    long
FROM {{ source('<bigquery_dataset_id_main>', 'circuits_2022_ext') }}
UNION ALL
SELECT 
    "2023" AS constructor_year,
    circuitKeyId AS circuit_keyId,
    season,
    circuitId AS circuit_id,
    circuitName AS circuit_name,
    country,
    locality,
    lat,
    long
FROM {{ source('<bigquery_dataset_id_main>', 'circuits_2023_ext') }}
UNION ALL
SELECT 
    "2024" AS constructor_year,
    circuitKeyId AS circuit_keyId,
    season,
    circuitId AS circuit_id,
    circuitName AS circuit_name,
    country,
    locality,
    lat,
    long
FROM {{ source('<bigquery_dataset_id_main>', 'circuits_2024_ext') }}