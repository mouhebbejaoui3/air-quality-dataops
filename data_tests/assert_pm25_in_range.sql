-- Le test échoue s'il retourne des lignes.
select * from {{ ref('stg_pollution') }}
where pm2_5_ugm3 < 0 or pm2_5_ugm3 > 500
   or pm10_ugm3 < 0 or pm10_ugm3 > 1000
