"""Orchestration Prefect : exécute le pipeline chaque jour à 06:00 (UTC).

    python flow.py          # exécute une fois maintenant, puis reste actif et planifie chaque jour
    python flow.py --now    # exécute une seule fois et s'arrête
"""
import subprocess
import sys

from prefect import flow, task

from run_pipeline import STEPS


@task
def run_step(title, command):
    """Une étape du pipeline. Si elle échoue, le flux s'arrête et Prefect marque l'exécution en échec."""
    result = subprocess.run(command, capture_output=True, text=True)
    print(result.stdout)
    if result.returncode != 0:
        print(result.stderr)
        raise RuntimeError(f"Étape échouée : {title}")


@flow(name="air-quality-daily", log_prints=True)
def daily_pipeline():
    for title, command in STEPS:
        # L'ingestion appelle des APIs externes : on réessaie 2 fois si le réseau a un souci.
        retries = 2 if command[-1] == "fetch_data.py" else 0
        run_step.with_options(name=title, retries=retries, retry_delay_seconds=60)(title, command)


if __name__ == "__main__":
    daily_pipeline()
    if "--now" not in sys.argv:
        daily_pipeline.serve(name="daily-0600-utc", cron="0 6 * * *")
