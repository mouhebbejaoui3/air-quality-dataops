import sys

import duckdb
import pandas as pd
import pandera.errors

from pipeline.schema import RAW_POLLUTION, RAW_WEATHER

WAREHOUSE = "warehouse.duckdb"

# table brute -> (fichier CSV, schéma de validation)
SOURCES = {
    "pollution": ("data/pollution_cities.csv", RAW_POLLUTION),
    "weather": ("data/weather_cities.csv", RAW_WEATHER),
}


def load(table, path, schema, con):
    """Extract + Load: vérifie le fichier, puis le copie tel quel dans le warehouse."""
    try:
        schema.validate(pd.read_csv(path), lazy=True)
    except pandera.errors.SchemaErrors as error:
        print(f"REFUSED: {path} does not match the expected schema")
        print(error.failure_cases[["column", "check", "failure_case"]].to_string(index=False))
        sys.exit(1)

    con.execute(
        f"""
        CREATE OR REPLACE TABLE raw.{table} AS
        SELECT
            *,
            row_number() OVER () AS _row_number,
            '{path}' AS _source_file,
            current_timestamp AS _loaded_at
        FROM read_csv('{path}', all_varchar = true)
        """
    )
    n = con.execute(f"SELECT count(*) FROM raw.{table}").fetchone()[0]
    print(f"Loaded {n} rows from {path} into raw.{table}")


def main():
    con = duckdb.connect(WAREHOUSE)
    con.execute("CREATE SCHEMA IF NOT EXISTS raw")
    for table, (path, schema) in SOURCES.items():
        load(table, path, schema, con)
    con.close()


if __name__ == "__main__":
    main()
