"""Schémas de validation des fichiers bruts."""
import pandera.pandas as pa

CITIES = ["Tunis", "Bizerte", "Sfax"]
ISO_HOUR = r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}$"

RAW_POLLUTION = pa.DataFrameSchema(
    {
        "city": pa.Column(str, pa.Check.isin(CITIES), nullable=False),
        "time": pa.Column(str, pa.Check.str_matches(ISO_HOUR), nullable=False),
        "pm2_5": pa.Column(float, pa.Check.in_range(0, 1000), nullable=False, coerce=True),
        "pm10": pa.Column(float, pa.Check.in_range(0, 2000), nullable=False, coerce=True),
    },
    strict=True,
)

RAW_WEATHER = pa.DataFrameSchema(
    {
        "city": pa.Column(str, pa.Check.isin(CITIES), nullable=False),
        "time": pa.Column(str, pa.Check.str_matches(ISO_HOUR), nullable=False),
        "temperature_2m": pa.Column(float, pa.Check.in_range(-10, 55), nullable=False, coerce=True),
        "relative_humidity_2m": pa.Column(float, pa.Check.in_range(0, 100), nullable=False, coerce=True),
    },
    strict=True,
)