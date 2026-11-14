"""Lance toute la plateforme, étape par étape, et s'arrête dès qu'une étape échoue."""
import subprocess
import sys

STEPS = [
    ("1. Ingestion depuis les APIs", ["python", "fetch_data.py"]),
    ("2. Contrats de données", ["python", "check_contracts.py"]),
    ("3. Modèles dbt", ["dbt", "run", "--profiles-dir", "."]),
    ("4. Tests dbt", ["dbt", "test", "--profiles-dir", "."]),
    ("5. Rapport", ["python", "report_md.py"]),
    ("6. Alerte PM2.5", ["python", "alert.py"]),
]


def main():
    for title, command in STEPS:
        print(f"\n=== {title} ===", flush=True)
        result = subprocess.run(command)
        if result.returncode != 0:
            print(f"\nECHEC à l'étape : {title}", flush=True)
            sys.exit(result.returncode)
    print("\nPipeline terminé avec succès.", flush=True)


if __name__ == "__main__":
    main()
