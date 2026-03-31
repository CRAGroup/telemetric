"""Hourly data aggregation."""

from __future__ import annotations

from celery import shared_task
from sqlalchemy import text

from ...core.database.connection import get_session


@shared_task(name="telemetric_system.tasks.scheduled.aggregate_hourly_data", autoretry_for=(Exception,), retry_backoff=2, max_retries=3)
def aggregate_hourly_data() -> dict:
    session = get_session()
    try:
        # For Timescale continuous aggregates, refresh policies handle it.
        # If using manual aggregates, run refresh calls here.
        session.execute(text("SELECT 1"))
        return {"status": "ok"}
    finally:
        session.close()
