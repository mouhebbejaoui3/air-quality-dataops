# Qualité de l'air et météo : villes tunisiennes

Sources : Open-Meteo Air Quality API (PM2.5, PM10, données modélisées CAMS) et Open-Meteo Weather API.
OpenAQ n'a pas de stations en Tunisie, d'où ce choix.

## Lancer le pipeline

    pip install -r requirements.txt
    python load_raw.py                      # CSV -> DuckDB (raw.pollution, raw.weather)
    dbt run  --profiles-dir .               # staging -> intermediate -> marts
    dbt test --profiles-dir .               # tests de qualité

Toutes les commandes se lancent depuis ce dossier.

## Questions métier
1. Quelle ville est la plus polluée ? -> `mart_city_pollution` (avg_pm25, pollution_rank)
2. La température influence-t-elle la pollution ? -> `mart_city_pollution` (corr_pm25_temperature)
3. Quels jours ont les pires pics ? -> `mart_daily_pollution` (worst_day_rank)

## Limites
- Données modélisées, pas des mesures de capteurs.
- Période courte (7 au 18 novembre 2026), dont une partie en prévision.
