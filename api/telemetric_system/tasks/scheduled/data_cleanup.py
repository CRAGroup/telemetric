"""Data archival/cleanup."""

from __future__ import annotations

from celery import shared_task
from datetime import datetime, timedelta

from ...core.database.connection import get_session


@shared_task(name="telemetric_system.tasks.scheduled.archive_old_data", autoretry_for=(Exception,), retry_backoff=2, max_retries=3)
def archive_old_data(days: int = 180) -> dict:
    cutoff = datetime.utcnow() - timedelta(days=days)
    session = get_session()
    try:
        # Placeholder: move old telemetry to cold storage or delete
        count = session.execute("DELETE FROM telemetry_data WHERE timestamp_utc < :cutoff RETURNING id", {"cutoff": cutoff}).rowcount  # type: ignore[assignment]
        session.commit()
        return {"archived": count or 0}
    finally:
        session.close()
