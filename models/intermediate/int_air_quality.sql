-- Jointure pollution + météo sur ville + heure.
-- Inner join : on garde seulement les heures présentes dans les deux sources.
select
    p.city,
    p.observed_at,
    cast(p.observed_at as date)                         as observed_date,
    p.pm2_5_ugm3,
    p.pm10_ugm3,
    w.temperature_c,
    w.humidity_pct,
    p.pm2_5_ugm3 > {{ var('pm25_threshold') }}          as is_pm25_alert
from {{ ref('stg_pollution') }} as p
inner join {{ ref('stg_weather') }} as w
    on  p.city = w.city
    and p.observed_at = w.observed_at
