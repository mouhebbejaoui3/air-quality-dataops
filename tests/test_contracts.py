"""Les contrats de données collent aux fichiers, et un fichier invalide est détecté."""
import pandas as pd

from check_contracts import check


def test_pollution_contract_matches_the_data():
    assert check("contracts/pollution.yaml") == []


def test_weather_contract_matches_the_data():
    assert check("contracts/weather.yaml") == []


def test_contract_detects_a_missing_column(tmp_path, monkeypatch):
    broken = pd.read_csv("data/pollution_cities.csv").drop(columns=["pm10"])
    broken_path = tmp_path / "broken.csv"
    broken.to_csv(broken_path, index=False)

    contract = open("contracts/pollution.yaml", encoding="utf-8").read()
    contract = contract.replace("./data/pollution_cities.csv", str(broken_path).replace("\\", "/"))
    contract_path = tmp_path / "pollution.yaml"
    contract_path.write_text(contract, encoding="utf-8")

    assert check(str(contract_path)) != []
