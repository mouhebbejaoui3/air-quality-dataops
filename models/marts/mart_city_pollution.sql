-- Q1 : quelle ville est la plus polluée ?
-- Q2 : la température influence-t-elle la pollution ? (corrélation par ville)
select
    city,
    count(*)                                                    as n_hours,
    round(avg(pm2_5_ugm3), 1)                                   as avg_pm25,
    round(max(pm2_5_ugm3), 1)                                   as max_pm25,
    round(avg(pm10_ugm3), 1)                                    as avg_pm10,
    sum(case when is_pm25_alert then 1 else 0 end)              as hours_above_threshold,
    round(100.0 * avg(case when is_pm25_alert then 1 else 0 end), 1) as pct_hours_above_threshold,
    round(avg(temperature_c), 1)                                as avg_temperature_c,
    round(corr(pm2_5_ugm3, temperature_c), 2)                   as corr_pm25_temperature,
    round(corr(pm2_5_ugm3, humidity_pct), 2)                    as corr_pm25_humidity,
    rank() over (order by avg(pm2_5_ugm3) desc)                 as pollution_rank
from {{ ref('int_air_quality') }}
group by city
