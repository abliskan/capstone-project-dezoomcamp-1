{{ 
    config(
        materialized='table'
    )
}}

WITH source_data AS (
    SELECT DISTINCT 
      race_result_sk,
      driver_sk,
      constructor_sk,
      race_resultid,
      season,
      round,
      race_name,
      driver_id,
      driver_name,
      constructor_id,
      constructor_name,
      grid,
      position,
      points,
      status,
      laps,
      fastest_rank,
      fastest_lap,
      fastest_time,
      fastest_speed,
      race_date,
      year,
      month,
      date_of_birth,
      nationality,
    FROM {{ ref('dim_race_result') }}
),

source_data_main AS ( 
    SELECT 
      sd_rr.race_result_sk,
      sd_rr.driver_sk,
      sd_rr.constructor_sk,
      sd_rr.season,
      sd_rr.round,
      sd_rr.race_name,
      sd_rr.driver_id,
      sd_rr.driver_name,
      sd_rr.constructor_id,
      sd_rr.constructor_name,
      sd_rr.grid,
      sd_rr.position,
      sd_rr.points,
      sd_rr.status,
      sd_rr.laps,
      sd_rr.fastest_rank,
      sd_rr.fastest_lap,
      sd_rr.fastest_time,
      sd_rr.fastest_speed,
      sd_rr.race_date,
      sd_rr.year,
      sd_rr.month,
      sd_rr.date_of_birth,
      sd_rr.nationality,
      dd_pts.stop,
      dd_pts.time,
      dd_pts.duration
FROM source_data sd_rr
LEFT JOIN {{ ref('dim_pitstop') }} dd_pts
ON sd_rr.driver_id = dd_pts.driver_id
)

SELECT * FROM source_data_main