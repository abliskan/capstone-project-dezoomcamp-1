{{ 
    config(
        materialized='table'
    )
}}

WITH source_data AS (
    SELECT *
    FROM {{ ref('stg_race_result') }}
)

SELECT 
  {{ dbt_utils.generate_surrogate_key(['race_resultid', 'race_name']) }} AS race_result_sk,
  dm_dd.driver_sk,
  dd_ctr.constructor_sk,
  stg_rr.season,
  stg_rr.race_resultid,
  stg_rr.round,
  stg_rr.race_name,
  stg_rr.driver_id,
  stg_rr.driver_name,
  stg_rr.constructor_id,
  stg_rr.constructor_name,
  stg_rr.grid,
  stg_rr.position,
  stg_rr.points,
  stg_rr.status,
  stg_rr.laps,
  stg_rr.fastest_rank,
  stg_rr.fastest_lap,
  stg_rr.fastest_time,
  stg_rr.fastest_speed,
  stg_rr.race_date,
  stg_rr.year,
  stg_rr.month,
  dm_dd.date_of_birth,
  dm_dd.nationality,
FROM source_data stg_rr
LEFT JOIN {{ ref('dim_constructors') }} dd_ctr
ON stg_rr.constructor_id = dd_ctr.constructor_id
LEFT JOIN {{ ref('dim_driver') }} dm_dd
ON stg_rr.driver_id = dm_dd.driver_id