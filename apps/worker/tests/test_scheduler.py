from datetime import UTC, datetime

from worker.main import schedule_next


def test_schedule_next_is_30_minute_step():
    now = datetime(2026, 1, 1, 12, 0, tzinfo=UTC)
    assert schedule_next(now).isoformat() == "2026-01-01T12:30:00+00:00"
