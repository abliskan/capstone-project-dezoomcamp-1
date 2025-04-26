{{ 
    config(
        materialized='view'
    )
}}

SELECT 
    "2020" AS pitstop_year,
    pitstopId AS pitstop_id,
    season,
    round,
    raceName AS race_name,
    date,
    CAST(driverId AS STRING) AS driver_id,
    stop,
    lap,
    time,
    duration
FROM {{ source('<bigquery_dataset_id_main>', 'pitstop_2020_ext') }}
UNION ALL
SELECT 
    "2021" AS pitstop_year,
    pitstopId AS pitstop_id,
    season,
    round,
    raceName AS race_name,
    date,
    CAST(driverId AS STRING) AS driver_id,
    stop,
    lap,
    time,
    duration
FROM {{ source('<bigquery_dataset_id_main>', 'pitstop_2021_ext') }}
UNION ALL
SELECT 
    "2022" AS pitstop_year,
    pitstopId AS pitstop_id,
    season,
    round,
    raceName AS race_name,
    date,
    CAST(driverId AS STRING) AS driver_id,
    stop,
    lap,
    time,
    duration
FROM {{ source('<bigquery_dataset_id_main>', 'pitstop_2022_ext') }}
UNION ALL
SELECT 
    "2023" AS pitstop_year,
    pitstopId AS pitstop_id,
    season,
    round,
    raceName AS race_name,
    date,
    CAST(driverId AS STRING) AS driver_id,
    stop,
    lap,
    time,
    duration
FROM {{ source('<bigquery_dataset_id_main>', 'pitstop_2023_ext') }}
UNION ALL
SELECT 
    "2024" AS pitstop_year,
    pitstopId AS pitstop_id,
    season,
    round,
    raceName AS race_name,
    date,
    CAST(driverId AS STRING) AS driver_id,
    stop,
    lap,
    time,
    duration
FROM {{ source('<bigquery_dataset_id_main>', 'pitstop_2024_ext') }}