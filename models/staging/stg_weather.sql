select
    trim(city)                              as city,
    cast("time" as timestamp)               as observed_at,
    cast(temperature_2m as double)          as temperature_c,
    cast(relative_humidity_2m as double)    as humidity_pct
from {{ source('raw', 'weather') }}
