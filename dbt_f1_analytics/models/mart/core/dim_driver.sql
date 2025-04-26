{{ 
    config(
        materialized='table'
    )
}}

WITH source_data AS (
    SELECT *
    FROM {{ ref('stg_driver') }}
)

SELECT
  {{ dbt_utils.generate_surrogate_key(['driver_keyid', 'date_of_birth']) }} AS driver_sk,
  cast(season as numeric) as season,
  driver_id,
  driver_name,
  cast(date_of_birth as DATE) as date_of_birth,
  nationality
FROM source_data