select * from {{ ref('stg_weather') }}
where temperature_c < -10 or temperature_c > 55
   or humidity_pct < 0 or humidity_pct > 100
