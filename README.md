# Qualité de l'air et météo : villes tunisiennes

Plateforme DataOps : les données de pollution (PM2.5, PM10) et de météo de Tunis, Sfax et Bizerte
sont téléchargées depuis l'API Open-Meteo, vérifiées, transformées avec dbt, puis résumées dans un rapport.

Sources : Open-Meteo Air Quality API (données modélisées CAMS) et Open-Meteo Weather API.
OpenAQ n'a pas de stations en Tunisie, d'où ce choix.

## Tout lancer en une commande

    docker compose up --build

Le conteneur exécute le pipeline une première fois, puis le planifie **chaque jour à 06:00 (UTC)** avec Prefect.
Pour l'arrêter : `Ctrl+C`, puis `docker compose down`.

Les étapes : ingestion sans doublons, contrats, `dbt run`, `dbt test`, santé des données (`health.md`), rapport, alerte PM2.5.
Si une étape échoue, la suite est bloquée. L'ingestion est réessayée 2 fois en cas de problème réseau.

## Lancer sans Docker

    pip install -r requirements.txt
    python run_pipeline.py      # une exécution simple
    python flow.py --now        # une exécution via Prefect
    python flow.py              # exécution + planification quotidienne

Ou étape par étape :

    python fetch_data.py                    # APIs -> DuckDB (raw.pollution, raw.weather), sans doublons
    python check_contracts.py               # contrats de données
    dbt run  --profiles-dir .               # staging -> intermediate -> marts
    dbt test --profiles-dir .               # tests de qualité
    python check_health.py                  # fraîcheur et complétude -> health.md (bloque si problème)
    python report_md.py                     # rapport Markdown
    python alert.py                         # alerte PM2.5

`load_raw.py` charge les CSV du dossier `data/` : c'est le chemin utilisé par la CI, car il ne dépend pas d'Internet.

## Questions métier
1. Quelle ville est la plus polluée ? -> `mart_city_pollution` (avg_pm25, pollution_rank)
2. La température influence-t-elle la pollution ? -> `mart_city_pollution` (corr_pm25_temperature)
3. Quels jours ont les pires pics ? -> `mart_daily_pollution` (worst_day_rank)

## Qualité
- Validation du schéma à l'entrée (pandera)
- Contrats de données dans `contracts/`
- 16 tests dbt
- CI GitHub Actions sur chaque pull request

## Limites
- Données modélisées, pas des mesures de capteurs.
- Les derniers jours sont des prévisions, qui changent d'un téléchargement à l'autre.
