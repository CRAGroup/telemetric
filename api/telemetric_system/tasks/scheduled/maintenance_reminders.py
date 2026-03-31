"""Maintenance reminder scheduling."""

from __future__ import annotations

from celery import shared_task
from datetime import datetime

from ...services.analytics.predictive import PredictiveMaintenanceService
from ...services.alerts.notification_service import NotificationService, NotificationPrefs
from ...core.database.connection import get_session
from ...models.vehicle import Vehicle


@shared_task(name="telemetric_system.tasks.scheduled.send_maintenance_reminders", autoretry_for=(Exception,), retry_backoff=2, max_retries=3)
def send_maintenance_reminders() -> dict:
    session = get_session()
    try:
        svc = PredictiveMaintenanceService()
        notifier = NotificationService()
        vehicles = session.query(Vehicle).all()
        sent = 0
        for v in vehicles:
            res = svc.analyze_vehicle(v.id)
            if res["urgency"]["level"] == "high":
                user = {"id": v.driver_id or 0, "email": "ops@example.com", "notification_prefs": NotificationPrefs(email=True)}
                notifier.queue(user, "Maintenance Reminder", f"Vehicle {v.vehicle_id} due: {res['schedule']}")
                sent += 1
        notifier.flush()
        return {"reminders_sent": sent}
    finally:
        session.close()
