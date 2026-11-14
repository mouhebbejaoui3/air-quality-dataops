-- Q3 : quels jours ont les pires niveaux de pollution ?
select
    city,
    observed_date,
    round(avg(pm2_5_ugm3), 1)                           as avg_pm25,
    round(max(pm2_5_ugm3), 1)                           as max_pm25,
    round(max(pm10_ugm3), 1)                            as max_pm10,
    sum(case when is_pm25_alert then 1 else 0 end)      as hours_above_threshold,
    round(avg(temperature_c), 1)                        as avg_temperature_c,
    row_number() over (order by max(pm2_5_ugm3) desc)   as worst_day_rank
from {{ ref('int_air_quality') }}
group by city, observed_date
