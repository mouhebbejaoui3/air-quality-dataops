select city, observed_at, count(*) as n
from {{ ref('int_air_quality') }}
group by city, observed_at
having count(*) > 1
