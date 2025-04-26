{{ 
    config(
        materialized='view'
    )
}}

SELECT 
    "2020" AS constructor_performance_year,
    constructorPerfKeyId AS constructor_perf_keyid,
    season,
    constructorId AS constructor_id,
    constructorName AS constructor_name,
    position,
    points,
    wins,
    nationality,
    CAST(url  AS STRING) AS url
FROM {{ source('<bigquery_dataset_id_main>', 'constructor_performance_2020_ext') }}
UNION ALL
SELECT 
    "2021" AS constructor_performance_year,
    constructorPerfKeyId AS constructor_perf_keyid,
    season,
    constructorId AS constructor_id,
    constructorName AS constructor_name,
    position,
    points,
    wins,
    nationality,
    CAST(url  AS STRING) AS url
FROM {{ source('<bigquery_dataset_id_main>', 'constructor_performance_2021_ext') }}
UNION ALL
SELECT 
    "2022" AS constructor_performance_year,
    constructorPerfKeyId AS constructor_perf_keyid,
    season,
    constructorId AS constructor_id,
    constructorName AS constructor_name,
    position,
    points,
    wins,
    nationality,
    CAST(url  AS STRING) AS url
FROM {{ source('<bigquery_dataset_id_main>', 'constructor_performance_2022_ext') }}
UNION ALL
SELECT 
    "2023" AS constructor_performance_year,
    constructorPerfKeyId AS constructor_perf_keyid,
    season,
    constructorId AS constructor_id,
    constructorName AS constructor_name,
    position,
    points,
    wins,
    nationality,
    CAST(url  AS STRING) AS url
FROM {{ source('<bigquery_dataset_id_main>', 'constructor_performance_2023_ext') }}
UNION ALL
SELECT 
    "2024" AS constructor_performance_year,
    constructorPerfKeyId AS constructor_perf_keyid,
    season,
    constructorId AS constructor_id,
    constructorName AS constructor_name,
    position,
    points,
    wins,
    nationality,
    CAST(url  AS STRING) AS url
FROM {{ source('<bigquery_dataset_id_main>', 'constructor_performance_2024_ext') }}