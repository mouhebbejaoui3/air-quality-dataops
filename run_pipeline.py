"""Lance toute la plateforme, étape par étape, et s'arrête dès qu'une étape échoue."""
import os
import shutil
import subprocess
import sys

# On utilise le Python et le dbt de l'environnement courant (.venv ou Docker),
# jamais un autre Python installé sur la machine.
PYTHON = sys.executable
DBT = shutil.which("dbt", path=os.path.dirname(PYTHON)) or "dbt"

STEPS = [
    ("1. Ingestion depuis les APIs", [PYTHON, "fetch_data.py"]),
    ("2. Contrats de données", [PYTHON, "check_contracts.py"]),
    ("3. Modèles dbt", [DBT, "run", "--profiles-dir", "."]),
    ("4. Tests dbt", [DBT, "test", "--profiles-dir", "."]),
    ("5. Santé des données", [PYTHON, "check_health.py"]),
    ("6. Rapport", [PYTHON, "report_md.py"]),
    ("7. Alerte PM2.5", [PYTHON, "alert.py"]),
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
