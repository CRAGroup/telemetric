"""Scheduled report generation tasks."""

from __future__ import annotations

from celery import shared_task

from ...services.data_processor.batch_processor import BatchProcessor
from ...api.routes.reports import _parse_dates, _build_report_rows  # reuse helpers


@shared_task(name="telemetric_system.tasks.scheduled.run_batch_processor")
def run_batch_processor() -> dict:
    bp = BatchProcessor()
    return bp.run()


@shared_task(name="telemetric_system.tasks.scheduled.generate_scheduled_reports", autoretry_for=(Exception,), retry_backoff=2, max_retries=3)
def generate_scheduled_reports() -> dict:
    # Stub: pull schedules from DB and generate
    return {"status": "ok"}
