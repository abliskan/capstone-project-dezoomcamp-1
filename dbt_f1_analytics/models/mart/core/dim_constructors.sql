{{ 
    config(
        materialized='table'
    )
}}

WITH source_data AS (
    SELECT *
    FROM {{ ref('stg_constructors') }}
)

SELECT
  {{ dbt_utils.generate_surrogate_key(['constructor_keyid']) }} AS constructor_sk,
  cast(season as numeric) as season,
  constructor_id,
  constructor_name,
  nationality
FROM source_data