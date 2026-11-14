"""Santé des données : fraîcheur, complétude, cohérence.

Écrit health.md (la page « santé des données ») et s'arrête avec le code 1 si un contrôle échoue.
Placé AVANT le rapport, il empêche de publier des chiffres douteux.
"""
import sys
from datetime import datetime, timedelta, timezone

import duckdb

WAREHOUSE = "warehouse.duckdb"
CITIES = ["Tunis", "Bizerte", "Sfax"]
TABLES = ["pollution", "weather"]

MAX_AGE_HOURS = 26      # une exécution par jour, plus une marge
MAX_MISSING_HOURS = 0   # aucune heure manquante entre la première et la dernière heure
MIN_MATCH_RATE = 0.90   # au moins 90 % des heures de pollution ont une météo correspondante


def is_fresh(age_minutes, max_hours):
    return age_minutes is not None and age_minutes <= max_hours * 60


def missing_hours(n_rows, span_hours):
    """Nombre d'heures manquantes dans une série horaire."""
    return span_hours + 1 - n_rows


def has_current_data(latest, now):
    """Vrai si la dernière heure disponible n'est pas en retard de plus d'une heure."""
    return latest is not None and latest >= now - timedelta(hours=1)


def one(con, sql):
    return con.execute(sql).fetchall()[0][0]


def run_checks(con, now):
    checks = []  # (nom, ok, détail)

    for table in TABLES:
        age = one(
            con,
            f"""
            select date_diff('minute', max(cast(_loaded_at as timestamp)), cast(current_timestamp as timestamp))
            from raw.{table}
            """,
        )
        detail = "aucun chargement" if age is None else f"dernier chargement il y a {age / 60:.1f} h (max {MAX_AGE_HOURS} h)"
        checks.append((f"Fraîcheur du chargement ({table})", is_fresh(age, MAX_AGE_HOURS), detail))

        latest = one(con, f"select max(observed_at) from stg_{table}")
        checks.append((f"Données à jour ({table})", has_current_data(latest, now), f"dernière heure disponible : {latest}"))

        present = {row[0] for row in con.execute(f"select distinct city from stg_{table}").fetchall()}
        missing = sorted(set(CITIES) - present)
        checks.append((f"Les 3 villes présentes ({table})", not missing, "toutes présentes" if not missing else f"manquantes : {missing}"))

        rows = con.execute(
            f"""
            select city, count(*), date_diff('hour', min(observed_at), max(observed_at))
            from stg_{table}
            group by city
            order by city
            """
        ).fetchall()
        gaps = {city: missing_hours(n, span) for city, n, span in rows}
        total = sum(gaps.values())
        detail = ", ".join(f"{city} : {gap}" for city, gap in gaps.items()) or "aucune donnée"
        checks.append((f"Aucune heure manquante ({table})", rows != [] and total <= MAX_MISSING_HOURS, f"heures manquantes par ville : {detail}"))

    in_pollution = one(con, "select count(*) from stg_pollution")
    in_joined = one(con, "select count(*) from int_air_quality")
    rate = in_joined / in_pollution if in_pollution else 0
    checks.append(("Pollution et météo bien jointes", rate >= MIN_MATCH_RATE, f"{in_joined} heures jointes sur {in_pollution} ({rate:.0%})"))

    return checks


def write_page(checks, now, path="health.md"):
    ok = all(c[1] for c in checks)
    lines = [
        "# Santé des données",
        "",
        f"Dernière vérification : {now:%Y-%m-%d %H:%M} UTC",
        "",
        f"**Statut global : {'OK' if ok else 'ECHEC'}**",
        "",
        "| Contrôle | Statut | Détail |",
        "| --- | --- | --- |",
    ]
    for name, passed, detail in checks:
        lines.append(f"| {name} | {'OK' if passed else 'ECHEC'} | {detail} |")
    with open(path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")


def main():
    con = duckdb.connect(WAREHOUSE, read_only=True)
    now = datetime.now(timezone.utc).replace(tzinfo=None)
    checks = run_checks(con, now)
    con.close()

    write_page(checks, now)
    for name, passed, detail in checks:
        print(f"{'OK   ' if passed else 'ECHEC'} {name} : {detail}")

    if not all(c[1] for c in checks):
        print("\nALERTE SANTE : des contrôles ont échoué, voir health.md")
        sys.exit(1)
    print("\nSanté des données : tout est OK (voir health.md)")


if __name__ == "__main__":
    main()
