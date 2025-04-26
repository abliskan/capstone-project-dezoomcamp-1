{{ 
    config(
        materialized='table'
    )
}}

WITH source_data AS (
    SELECT *
    FROM {{ ref('stg_pitstop') }}
)

SELECT
  {{ dbt_utils.generate_surrogate_key(['pitstop_id']) }} AS pitstop_sk,
  cast(season as numeric) as season,
  pitstop_id,
  cast(round as numeric) as round,
  race_name,
  cast(date as DATE) as date,
  driver_id,
  cast(stop as numeric) as stop,
  cast(lap as numeric) as lap,
  time,
  duration
FROM source_data