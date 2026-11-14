import duckdb
import yaml


def main():
    """Amélioration personnelle : alerte quand une ville dépasse le seuil de PM2.5."""
    with open("dbt_project.yml", encoding="utf-8") as f:
        threshold = yaml.safe_load(f)["vars"]["pm25_threshold"]

    con = duckdb.connect("warehouse.duckdb", read_only=True)
    summary = con.sql(
        """
        select city, count(*) as n_hours, max(pm2_5_ugm3) as peak, min(observed_at) as first_alert
        from int_air_quality
        where is_pm25_alert
        group by city
        order by n_hours desc
        """
    ).fetchall()

    if not summary:
        print(f"Aucune alerte : aucune ville au-dessus de {threshold} µg/m³.")
        return

    print(f"ALERTE PM2.5 : seuil de {threshold} µg/m³ dépassé\n")
    for city, n_hours, peak, first_alert in summary:
        print(f"- {city} : {n_hours} heures au-dessus du seuil, pic à {float(peak):.1f} µg/m³, "
              f"première alerte le {first_alert}")


if __name__ == "__main__":
    main()
