"""Les règles du contrôle de santé des données."""
from datetime import datetime, timedelta

from check_health import has_current_data, is_fresh, missing_hours


def test_recent_load_is_fresh():
    assert is_fresh(60, max_hours=26)


def test_old_load_is_not_fresh():
    assert not is_fresh(27 * 60, max_hours=26)


def test_no_load_is_not_fresh():
    assert not is_fresh(None, max_hours=26)


def test_complete_series_has_no_missing_hours():
    # 240 heures consécutives : la première et la dernière sont séparées de 239 heures
    assert missing_hours(240, 239) == 0


def test_series_with_gap_is_detected():
    assert missing_hours(238, 239) == 2


def test_data_up_to_now_is_current():
    now = datetime(2026, 11, 17, 12, 0)
    assert has_current_data(now + timedelta(days=2), now)


def test_old_data_is_not_current():
    now = datetime(2026, 11, 17, 12, 0)
    assert not has_current_data(now - timedelta(hours=5), now)


def test_no_data_is_not_current():
    assert not has_current_data(None, datetime(2026, 11, 17, 12, 0))
