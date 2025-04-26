 {{
  config(
    materialized = 'table',
  )
}}

WITH race_results AS (
  SELECT * FROM {{ ref('fct_f1_race_data') }}
),

constructors AS (
  SELECT * FROM {{ ref('dim_constructors') }}
),

top_constructor AS (
  SELECT
    cs.constructor_id,
    cs.constructor_name,
    rr.season,
    COUNT(*) AS total_entries,
    SUM(rr.points) AS total_points,
    -- Count races where constructor got placed 1st
    SUM(CASE 
          WHEN rr.position = 1 
          THEN 1 
          ELSE 0 
        END) AS wins
  FROM race_results rr
  JOIN constructors cs
  ON rr.constructor_id = cs.constructor_id
  GROUP BY 
      rr.season, 
      cs.constructor_id, 
      cs.constructor_name
),

ranked_constructors AS (
    SELECT
        season,
        constructor_id,
        constructor_name,
        total_entries,
        total_points,
        wins,
        SAFE_DIVIDE(wins, total_entries) AS win_ratio,
        SAFE_DIVIDE(total_points, total_entries) AS avg_points_per_entry,
        RANK() OVER (PARTITION BY season ORDER BY total_points DESC) AS points_rank
    FROM top_constructor
)

SELECT
    season,
    constructor_id,
    constructor_name,
    total_entries,
    total_points,
    wins,
    ROUND(win_ratio * 100, 2) AS win_percentage,
    ROUND(avg_points_per_entry, 2) AS avg_points_per_entry,
    points_rank
FROM ranked_constructors
ORDER BY 
    season DESC,
    wins DESC,
    total_points DESC