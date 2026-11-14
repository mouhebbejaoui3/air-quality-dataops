import sys

import duckdb


def strength(corr):
    """Traduit une corrélation en mots simples."""
    if corr is None:
        return "non calculable"
    size = abs(float(corr))
    if size < 0.3:
        return "faible"
    if size < 0.6:
        return "moyenne"
    return "forte"


def main(expected_top_city=None):
    """Affiche le rapport en Markdown, et s'arrête si la ville la plus polluée n'est pas celle attendue."""
    con = duckdb.connect("warehouse.duckdb", read_only=True)

    cities = con.sql(
        """
        select city, avg_pm25, max_pm25, hours_above_threshold, pct_hours_above_threshold
        from mart_city_pollution
        order by pollution_rank
        """
    ).fetchall()

    corrs = con.sql(
        """
        select city, corr_pm25_temperature, corr_pm25_humidity
        from mart_city_pollution
        order by pollution_rank
        """
    ).fetchall()

    days = con.sql(
        """
        select worst_day_rank, city, observed_date, max_pm25, hours_above_threshold
        from mart_daily_pollution
        order by worst_day_rank
        limit 5
        """
    ).fetchall()

    print("# Qualité de l'air et météo : villes tunisiennes\n")

    print("## 1. Quelle ville est la plus polluée ?\n")
    print("| Ville | PM2.5 moyen | PM2.5 max | Heures > seuil | % des heures |")
    print("| --- | ---: | ---: | ---: | ---: |")
    for city, avg, mx, hours, pct in cities:
        print(f"| {city} | {float(avg):.1f} | {float(mx):.1f} | {int(hours)} | {float(pct):.1f} |")
    top = cities[0][0]
    most_hours = max(cities, key=lambda row: row[3])[0]
    print(f"\n**{top}** a la moyenne de PM2.5 la plus haute. "
          f"**{most_hours}** a le plus d'heures au-dessus du seuil.")

    print("\n## 2. La température influence-t-elle la pollution ?\n")
    print("| Ville | Corrélation PM2.5 / température | Intensité | Corrélation PM2.5 / humidité |")
    print("| --- | ---: | --- | ---: |")
    for city, c_temp, c_hum in corrs:
        c_temp_txt = "n/a" if c_temp is None else f"{float(c_temp):.2f}"
        c_hum_txt = "n/a" if c_hum is None else f"{float(c_hum):.2f}"
        print(f"| {city} | {c_temp_txt} | {strength(c_temp)} | {c_hum_txt} |")
    print("\nUne corrélation proche de 0 signifie qu'il n'y a pas de lien net sur cette période.")

    print("\n## 3. Quels jours ont les pires pics ?\n")
    print("| Rang | Ville | Jour | PM2.5 max | Heures > seuil |")
    print("| ---: | --- | --- | ---: | ---: |")
    for rank, city, day, mx, hours in days:
        print(f"| {int(rank)} | {city} | {day} | {float(mx):.1f} | {int(hours)} |")

    print("\n## Limites\n")
    print("- Données modélisées (Open-Meteo / CAMS), pas des mesures de capteurs.")
    print("- Période courte, et les derniers jours sont des prévisions.")

    if expected_top_city is not None and top != expected_top_city:
        print(f"\nREGRESSION: expected {expected_top_city}, got {top}")
        sys.exit(1)


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else None)
