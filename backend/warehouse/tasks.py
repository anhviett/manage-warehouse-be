from __future__ import annotations

from celery import shared_task

from warehouse.models import Equipment
from warehouse.services.operations import evaluate_equipment_health


@shared_task(name="warehouse.tasks.predict_equipment_failure")
def predict_equipment_failure() -> dict[str, int]:
    evaluations = [evaluate_equipment_health(equipment) for equipment in Equipment.objects.all()]

    high_risk_count = sum(1 for item in evaluations if item["risk_level"] == "high")
    medium_risk_count = sum(1 for item in evaluations if item["risk_level"] == "medium")

    return {
        "equipment_count": len(evaluations),
        "high_risk_count": high_risk_count,
        "medium_risk_count": medium_risk_count,
    }