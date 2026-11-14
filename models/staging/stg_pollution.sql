-- Nettoyage : types corrects, noms explicites, une ligne = une ville + une heure.
select
    trim(city)                  as city,
    cast("time" as timestamp)   as observed_at,
    cast(pm2_5 as double)       as pm2_5_ugm3,
    cast(pm10 as double)        as pm10_ugm3
from {{ source('raw', 'pollution') }}
