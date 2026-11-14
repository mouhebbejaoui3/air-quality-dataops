"""Ingestion automatique : appelle les 2 APIs Open-Meteo pour les 3 villes et charge DuckDB.

Idempotent : on peut relancer ce script autant de fois qu'on veut, il ne crée aucun doublon.
Clé d'unicité : (ville, heure). Si une heure existe déjà (par exemple une prévision),
elle est remplacée par la valeur la plus récente.
"""
import sys
import time

import duckdb
import pandas as pd
import pandera.errors
import requests

from pipeline.schema import RAW_POLLUTION, RAW_WEATHER

WAREHOUSE = "warehouse.duckdb"
PAST_DAYS = 7
FORECAST_DAYS = 3

CITIES = {
    "Tunis": (36.82, 10.17),
    "Bizerte": (37.27, 9.87),
    "Sfax": (34.74, 10.76),
}

SOURCES = {
    "pollution": {
        "url": "https://air-quality-api.open-meteo.com/v1/air-quality",
        "variables": ["pm2_5", "pm10"],
        "schema": RAW_POLLUTION,
    },
    "weather": {
        "url": "https://api.open-meteo.com/v1/forecast",
        "variables": ["temperature_2m", "relative_humidity_2m"],
        "schema": RAW_WEATHER,
    },
}


def call_api(url, params, attempts=3):
    """Appelle l'API, avec quelques essais si le réseau a un souci."""
    for attempt in range(1, attempts + 1):
        try:
            response = requests.get(url, params=params, timeout=30)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as error:
            print(f"  essai {attempt}/{attempts} échoué : {error}")
            if attempt == attempts:
                raise
            time.sleep(2 * attempt)


def parse_hourly(city, payload, variables):
    """Transforme la réponse JSON de l'API en tableau (une ligne par ville et par heure)."""
    hourly = payload["hourly"]
    data = {"city": city, "time": hourly["time"]}
    for variable in variables:
        data[variable] = hourly[variable]
    return pd.DataFrame(data)


def fetch_table(name):
    """Télécharge une source pour toutes les villes."""
    source = SOURCES[name]
    frames = []
    for city, (latitude, longitude) in CITIES.items():
        params = {
            "latitude": latitude,
            "longitude": longitude,
            "hourly": ",".join(source["variables"]),
            "past_days": PAST_DAYS,
            "forecast_days": FORECAST_DAYS,
            "timezone": "GMT",
        }
        print(f"  {name} : {city}")
        payload = call_api(source["url"], params)
        frames.append(parse_hourly(city, payload, source["variables"]))

    df = pd.concat(frames, ignore_index=True)
    before = len(df)
    df = df.dropna(subset=source["variables"]).drop_duplicates(["city", "time"])
    if len(df) < before:
        print(f"  {before - len(df)} lignes ignorées (valeurs manquantes ou doublons)")
    return df


def upsert(con, table, df, variables, url):
    """Remplace les heures déjà présentes, ajoute les nouvelles : jamais de doublon."""
    columns = ["city", "time"] + variables
    select_list = ", ".join(f'cast("{c}" as varchar) as "{c}"' for c in columns)
    con.register("incoming", df)

    con.execute(
        f"""
        CREATE TABLE IF NOT EXISTS raw.{table} AS
        SELECT {select_list},
               cast(null AS varchar) AS _source_file,
               cast(null AS timestamp) AS _loaded_at
        FROM incoming WHERE false
        """
    )
    con.execute(
        f"""
        DELETE FROM raw.{table}
        WHERE (city, "time") IN (SELECT city, "time" FROM incoming)
        """
    )
    con.execute(
        f"""
        INSERT INTO raw.{table} BY NAME
        SELECT {select_list},
               '{url}' AS _source_file,
               current_timestamp AS _loaded_at
        FROM incoming
        """
    )
    con.unregister("incoming")


def count_duplicates(con, table):
    rows = con.execute(
        f"""
        SELECT count(*) FROM (
            SELECT city, "time" FROM raw.{table} GROUP BY 1, 2 HAVING count(*) > 1
        )
        """
    ).fetchall()
    return rows[0][0]


def main():
    con = duckdb.connect(WAREHOUSE)
    con.execute("CREATE SCHEMA IF NOT EXISTS raw")

    for name, source in SOURCES.items():
        print(f"Source {name}")
        try:
            df = fetch_table(name)
        except requests.RequestException as error:
            print(f"ECHEC : impossible de joindre l'API ({error})")
            sys.exit(1)

        try:
            source["schema"].validate(df, lazy=True)
        except pandera.errors.SchemaErrors as error:
            print(f"REFUSED: les données de {name} ne respectent pas le schéma attendu")
            print(error.failure_cases[["column", "check", "failure_case"]].to_string(index=False))
            sys.exit(1)

        upsert(con, name, df, source["variables"], source["url"])
        total = con.execute(f"SELECT count(*) FROM raw.{name}").fetchall()[0][0]
        duplicates = count_duplicates(con, name)
        print(f"  reçu {len(df)} lignes, raw.{name} contient {total} lignes, doublons : {duplicates}")
        if duplicates:
            print("ECHEC : des doublons existent dans la table")
            sys.exit(1)

    con.close()


if __name__ == "__main__":
    main()