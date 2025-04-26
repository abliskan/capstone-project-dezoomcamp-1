{{ 
    config(
        materialized='view'
    )
}}

SELECT 
    "2020" AS driver_year,
    driverKeyId AS driver_keyid,
    season,
    driverId AS driver_id,
    driverName AS driver_name,
    dateOfBirth AS date_of_birth,
    nationality
FROM {{ source('<bigquery_dataset_id_main>', 'driver_2020_ext') }}
UNION ALL
SELECT 
    "2021" AS driver_year,
    driverKeyId AS driver_keyid,
    season,
    driverId AS driver_id,
    driverName AS driver_name,
    dateOfBirth AS date_of_birth,
    nationality
FROM {{ source('<bigquery_dataset_id_main>', 'driver_2021_ext') }}
UNION ALL
SELECT 
    "2022" AS driver_year,
    driverKeyId AS driver_keyid,
    season,
    driverId AS driver_id,
    driverName AS driver_name,
    dateOfBirth AS date_of_birth,
    nationality
FROM {{ source('<bigquery_dataset_id_main>', 'driver_2022_ext') }}
UNION ALL
SELECT 
    "2023" AS driver_year,
    driverKeyId AS driver_keyid,
    season,
    driverId AS driver_id,
    driverName AS driver_name,
    dateOfBirth AS date_of_birth,
    nationality
FROM {{ source('<bigquery_dataset_id_main>', 'driver_2023_ext') }}
UNION ALL
SELECT 
    "2024" AS driver_year,
    driverKeyId AS driver_keyid,
    season,
    driverId AS driver_id,
    driverName AS driver_name,
    dateOfBirth AS date_of_birth,
    nationality
FROM {{ source('<bigquery_dataset_id_main>', 'driver_2024_ext') }}