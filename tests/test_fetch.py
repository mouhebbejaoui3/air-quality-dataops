"""La transformation de la réponse de l'API en tableau."""
from fetch_data import parse_hourly


def sample_payload():
    return {
        "hourly": {
            "time": ["2026-11-07T00:00", "2026-11-07T01:00"],
            "pm2_5": [9.6, 9.1],
            "pm10": [17.6, 15.3],
        }
    }


def test_parse_hourly_has_one_row_per_hour():
    df = parse_hourly("Tunis", sample_payload(), ["pm2_5", "pm10"])
    assert len(df) == 2


def test_parse_hourly_adds_the_city_column():
    df = parse_hourly("Sfax", sample_payload(), ["pm2_5", "pm10"])
    assert set(df["city"]) == {"Sfax"}


def test_parse_hourly_keeps_columns_in_order():
    df = parse_hourly("Tunis", sample_payload(), ["pm2_5", "pm10"])
    assert list(df.columns) == ["city", "time", "pm2_5", "pm10"]


def test_parse_hourly_keeps_missing_values_as_nan():
    payload = sample_payload()
    payload["hourly"]["pm2_5"][1] = None
    df = parse_hourly("Tunis", payload, ["pm2_5", "pm10"])
    assert df["pm2_5"].isna().sum() == 1
