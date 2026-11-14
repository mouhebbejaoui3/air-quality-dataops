"""Vérifie que chaque fichier de données respecte son contrat (colonnes, obligatoire, bornes)."""
import glob
import sys

import pandas as pd
import yaml


def check(contract_path):
    with open(contract_path, encoding="utf-8") as f:
        contract = yaml.safe_load(f)

    server = contract["servers"][0]
    df = pd.read_csv(server["path"])
    properties = contract["schema"][0]["properties"]
    errors = []

    expected = [p["name"] for p in properties]
    if list(df.columns) != expected:
        errors.append(f"colonnes attendues {expected}, trouvées {list(df.columns)}")
        return errors

    for p in properties:
        name, kind = p["name"], p["logicalType"]
        column = df[name]

        if p.get("required") and column.isna().any():
            errors.append(f"{name}: {int(column.isna().sum())} valeurs manquantes alors que required=true")

        if kind in ("integer", "number"):
            if not pd.api.types.is_numeric_dtype(column):
                errors.append(f"{name}: devrait être numérique")
                continue
            if kind == "integer" and not (column.dropna() % 1 == 0).all():
                errors.append(f"{name}: devrait contenir des entiers")
            options = p.get("logicalTypeOptions", {})
            if "minimum" in options and (column < options["minimum"]).any():
                errors.append(f"{name}: valeurs sous le minimum {options['minimum']}")
            if "maximum" in options and (column > options["maximum"]).any():
                errors.append(f"{name}: valeurs au-dessus du maximum {options['maximum']}")

    return errors


def main():
    failed = False
    for path in sorted(glob.glob("contracts/*.yaml")):
        errors = check(path)
        if errors:
            failed = True
            print(f"FAIL {path}")
            for error in errors:
                print(f"  - {error}")
        else:
            print(f"OK   {path}")
    if failed:
        sys.exit(1)


if __name__ == "__main__":
    main()
