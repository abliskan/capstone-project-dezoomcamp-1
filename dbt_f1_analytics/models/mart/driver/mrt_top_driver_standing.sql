 {{
  config(
    materialized = 'table',
  )
}}

WITH race_results AS (
  SELECT * FROM {{ ref('fct_f1_race_data') }}
),

drivers AS (
  SELECT * FROM {{ ref('dim_driver') }}
),

top_driver AS (
  SELECT
    ds.driver_id,
    ds.driver_name,
    rr.season,
    COUNT(*) AS total_races,
    SUM(rr.points) AS total_points,
    -- Count races where driver got placed 1st, 2nd, and 3rd
    SUM(CASE 
          WHEN rr.position = 1 
          THEN 1 
          ELSE 0 
        END) AS wins,
    SUM(CASE 
          WHEN rr.position = 2 
          THEN 1 
          ELSE 0 
        END) AS second_places,
    SUM(CASE 
          WHEN rr.position = 3 
          THEN 1 
          ELSE 0 
        END) AS third_places,
    SUM(CASE 
          WHEN rr.position IN (1, 2, 3) 
          THEN 1 
          ELSE 0 
        END) AS podium_finishes
  FROM race_results rr
  JOIN drivers ds
  ON rr.driver_id = ds.driver_id
  GROUP BY 
      rr.season, 
      ds.driver_id, 
      ds.driver_name
),

ranked_drivers AS (
    SELECT
        season,
        driver_id,
        driver_name,
        total_races,
        total_points,
        wins,
        second_places,
        third_places,
        podium_finishes,
        SAFE_DIVIDE(wins, total_races) AS win_ratio,
        SAFE_DIVIDE(podium_finishes, total_races) AS podium_ratio,
        SAFE_DIVIDE(total_points, total_races) AS avg_points_per_race,
        RANK() OVER (PARTITION BY season ORDER BY wins DESC, podium_finishes DESC, total_points DESC) AS win_rank,
        RANK() OVER (PARTITION BY season ORDER BY total_points DESC) AS points_rank
    FROM top_driver
)

SELECT 
    season,
    driver_id,
    driver_name,
    total_races,
    total_points,
    wins,
    second_places,
    third_places,
    podium_finishes,
    ROUND(win_ratio * 100, 2) AS win_percentage,
    ROUND(podium_ratio * 100, 2) AS podium_percentage,
    ROUND(avg_points_per_race, 2) AS avg_points_per_race,
    win_rank,
    points_rank
FROM ranked_drivers
ORDER BY season DESC,
    wins DESC,
    podium_finishes DESC,
    total_points DESC