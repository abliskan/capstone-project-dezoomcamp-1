{{ 
    config(
        materialized='view'
    )
}}

SELECT 
    "2020" AS driver_performance_year,
    driverPerfKeyId AS circuit_perf_keyid,
    season,
    driverId AS driver_id,
    driverName AS driver_name,
    constructorId AS constructor_id,
    constructorName AS constructor_name,
    position,
    points,
    wins
FROM {{ source('<bigquery_dataset_id_main>', 'driver_performance_2020_ext') }}
UNION ALL
SELECT 
    "2021" AS driver_performance_year,
    driverPerfKeyId AS circuit_perf_keyid,
    season,
    driverId AS driver_id,
    driverName AS driver_name,
    constructorId AS constructor_id,
    constructorName AS constructor_name,
    position,
    points,
    wins
FROM {{ source('<bigquery_dataset_id_main>', 'driver_performance_2021_ext') }}
UNION ALL
SELECT 
    "2022" AS driver_performance_year,
    driverPerfKeyId AS circuit_perf_keyid,
    season,
    driverId AS driver_id,
    driverName AS driver_name,
    constructorId AS constructor_id,
    constructorName AS constructor_name,
    position,
    points,
    wins
FROM {{ source('<bigquery_dataset_id_main>', 'driver_performance_2022_ext') }}
UNION ALL
SELECT 
    "2023" AS driver_performance_year,
    driverPerfKeyId AS circuit_perf_keyid,
    season,
    driverId AS driver_id,
    driverName AS driver_name,
    constructorId AS constructor_id,
    constructorName AS constructor_name,
    position,
    points,
    wins
FROM {{ source('<bigquery_dataset_id_main>', 'driver_performance_2023_ext') }}
UNION ALL
SELECT 
    "2024" AS driver_performance_year,
    driverPerfKeyId AS circuit_perf_keyid,
    season,
    driverId AS driver_id,
    driverName AS driver_name,
    constructorId AS constructor_id,
    constructorName AS constructor_name,
    position,
    points,
    wins
FROM {{ source('<bigquery_dataset_id_main>', 'driver_performance_2024_ext') }}