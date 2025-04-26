 {{
  config(
    materialized = 'table',
  )
}}

WITH race_results AS (
  SELECT * FROM {{ ref('fct_f1_race_data') }}
),

fastest_pistop AS (
  SELECT
      rr.season,
      rr.round,
      rr.race_name,
      rr.constructor_name,
      rr.driver_id,
      rr.grid,
      rr.position,
      rr.status,
      -- Convert pit_stop_duration string to FLOAT if it's stored as a string
      SAFE_CAST(rr.duration AS FLOAT64) AS pit_time,
      CASE 
        WHEN rr.status LIKE '%Finished%' OR rr.position IS NOT NULL 
        THEN 1
        ELSE 0
      END AS race_completed_flag
  FROM race_results rr
),

aggregated_performance AS (
  SELECT
      season,
      round,
      race_name,
      constructor_name,
      COUNT(DISTINCT driver_id) AS driver_count,
      AVG(CAST(grid AS FLOAT64)) AS avg_grid_position,
      AVG(CAST(position AS FLOAT64)) AS avg_finish_position,
      SUM(race_completed_flag) AS completed_races,
      COUNT(*) AS total_races,
      SAFE_DIVIDE(SUM(race_completed_flag), COUNT(*)) * 100 AS reliability_percentage,
      AVG(CAST(grid AS FLOAT64) - CAST(position AS FLOAT64)) AS avg_positions_gained,
      AVG(pit_time) AS avg_pit_time,
      MIN(pit_time) AS fastest_pit_time,
      MAX(pit_time) AS slowest_pit_time
  FROM fastest_pistop
  GROUP BY 
    season, 
    round, 
    race_name, 
    constructor_name
)

SELECT 
  season,
  round,
  race_name,
  constructor_name,
  driver_count,
  ROUND(avg_grid_position, 2) AS avg_grid_position,
  ROUND(avg_finish_position, 2) AS avg_finish_position,
  completed_races,
  total_races,
  ROUND(reliability_percentage, 2) AS reliability_percentage,
  ROUND(avg_positions_gained, 2) AS avg_positions_gained,
  ROUND(avg_pit_time, 3) AS avg_pit_time,
  ROUND(fastest_pit_time, 3) AS fastest_pit_time,
  ROUND(slowest_pit_time, 3) AS slowest_pit_time,
  RANK() OVER (PARTITION BY season, round ORDER BY avg_pit_time ASC) AS pit_efficiency_rank,
  RANK() OVER (PARTITION BY season, round ORDER BY reliability_percentage DESC, avg_positions_gained DESC) AS race_performance_rank
FROM aggregated_performance
ORDER BY 
    season DESC,
    round ASC,
    avg_pit_time ASC