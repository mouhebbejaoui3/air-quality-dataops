"""Les schémas d'entrée acceptent les bonnes données et refusent les mauvaises."""
import pandas as pd
import pandera.errors
import pytest

from pipeline.schema import RAW_POLLUTION, RAW_WEATHER


def good_pollution():
    return pd.DataFrame(
        {"city": ["Tunis", "Sfax"], "time": ["2026-11-07T00:00", "2026-11-07T01:00"], "pm2_5": [9.6, 12.0], "pm10": [17.6, 20.1]}
    )


def good_weather():
    return pd.DataFrame(
        {
            "city": ["Tunis", "Sfax"],
            "time": ["2026-11-07T00:00", "2026-11-07T01:00"],
            "temperature_2m": [15.4, 18.0],
            "relative_humidity_2m": [93, 80],
        }
    )


def test_good_pollution_is_accepted():
    RAW_POLLUTION.validate(good_pollution(), lazy=True)


def test_good_weather_is_accepted_with_integer_humidity():
    RAW_WEATHER.validate(good_weather(), lazy=True)


def test_unknown_city_is_refused():
    df = good_pollution()
    df.loc[0, "city"] = "Paris"
    with pytest.raises(pandera.errors.SchemaErrors):
        RAW_POLLUTION.validate(df, lazy=True)


def test_negative_pm25_is_refused():
    df = good_pollution()
    df.loc[0, "pm2_5"] = -5.0
    with pytest.raises(pandera.errors.SchemaErrors):
        RAW_POLLUTION.validate(df, lazy=True)


def test_bad_time_format_is_refused():
    df = good_pollution()
    df.loc[0, "time"] = "07/11/2026 00:00"
    with pytest.raises(pandera.errors.SchemaErrors):
        RAW_POLLUTION.validate(df, lazy=True)


def test_humidity_above_100_is_refused():
    df = good_weather()
    df.loc[0, "relative_humidity_2m"] = 140
    with pytest.raises(pandera.errors.SchemaErrors):
        RAW_WEATHER.validate(df, lazy=True)


def test_missing_value_is_refused():
    df = good_pollution()
    df.loc[0, "pm10"] = None
    with pytest.raises(pandera.errors.SchemaErrors):
        RAW_POLLUTION.validate(df, lazy=True)
