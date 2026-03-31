"""Celery application configuration and initialization."""

from __future__ import annotations

import os
from celery import Celery
from kombu import Exchange, Queue

broker_url = os.getenv("CELERY_BROKER_URL", "redis://localhost:6379/0")
backend_url = os.getenv("CELERY_RESULT_BACKEND", broker_url)

celery_app = Celery("telemetric_system", broker=broker_url, backend=backend_url, include=[
    "telemetric_system.tasks.scheduled.report_generation",
])
celery_app.conf.timezone = os.getenv("TZ", "UTC")

# Queues and routing
celery_app.conf.task_queues = (
    Queue("default", Exchange("default"), routing_key="default"),
    Queue("high", Exchange("high"), routing_key="high"),
    Queue("low", Exchange("low"), routing_key="low"),
)
celery_app.conf.task_default_queue = "default"
celery_app.conf.task_routes = {
    "telemetric_system.tasks.scheduled.run_batch_processor": {"queue": "low"},
    "telemetric_system.tasks.scheduled.archive_old_data": {"queue": "low"},
    "telemetric_system.tasks.scheduled.generate_scheduled_reports": {"queue": "default"},
    "telemetric_system.tasks.scheduled.send_maintenance_reminders": {"queue": "default"},
    "telemetric_system.tasks.scheduled.aggregate_hourly_data": {"queue": "high"},
    "telemetric_system.tasks.scheduled.backup_database": {"queue": "low"},
}

# Retries and timeouts
celery_app.conf.task_default_retry_delay = 10  # seconds
celery_app.conf.task_time_limit = 600  # hard limit
celery_app.conf.task_soft_time_limit = 540  # graceful soft timeout
celery_app.conf.task_acks_late = True
celery_app.conf.worker_max_tasks_per_child = 100

# Beat schedule
celery_app.conf.beat_schedule = {
    "run-batch-processor-hourly": {
        "task": "telemetric_system.tasks.scheduled.run_batch_processor",
        "schedule": 3600.0,
    },
    "archive-old-data-daily": {
        "task": "telemetric_system.tasks.scheduled.archive_old_data",
        "schedule": 24 * 3600.0,
    },
    "generate-scheduled-reports": {
        "task": "telemetric_system.tasks.scheduled.generate_scheduled_reports",
        "schedule": 3600.0,
    },
    "maintenance-reminders-daily": {
        "task": "telemetric_system.tasks.scheduled.send_maintenance_reminders",
        "schedule": 24 * 3600.0,
    },
    "aggregate-hourly-data": {
        "task": "telemetric_system.tasks.scheduled.aggregate_hourly_data",
        "schedule": 3600.0,
    },
    "backup-database-daily": {
        "task": "telemetric_system.tasks.scheduled.backup_database",
        "schedule": 24 * 3600.0,
    },
}

# Logging
celery_app.conf.worker_hijack_root_logger = False

# Flower monitoring: run with `celery -A telemetric_system.tasks.celery_app.celery_app flower`
