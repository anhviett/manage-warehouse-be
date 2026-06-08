from __future__ import annotations

from datetime import timedelta
from typing import Any

from django.utils import timezone

from warehouse.models import Equipment


def evaluate_equipment_health(equipment: Equipment) -> dict[str, Any]:
    runtime_ratio = equipment.runtime_hours / max(equipment.maintenance_interval_hours, 1)
    maintenance_overdue = False

    if equipment.last_maintenance is not None:
        maintenance_overdue = equipment.last_maintenance <= timezone.now() - timedelta(days=90)

    health_score = max(
        min(
            100 - (runtime_ratio * 35) - (15 if maintenance_overdue else 0),
            100,
        ),
        0,
    )

    if runtime_ratio >= 1.2 or health_score < 40:
        risk_level = "high"
        recommended_status = Equipment.STATUS_WARNING
    elif runtime_ratio >= 0.85 or health_score < 70 or maintenance_overdue:
        risk_level = "medium"
        recommended_status = Equipment.STATUS_MAINTENANCE
    else:
        risk_level = "low"
        recommended_status = Equipment.STATUS_OPERATIONAL

    return {
        "equipment_id": equipment.id,
        "equipment_code": equipment.code,
        "equipment_name": equipment.name,
        "warehouse_id": equipment.warehouse_id,
        "runtime_hours": round(float(equipment.runtime_hours), 2),
        "maintenance_interval_hours": round(float(equipment.maintenance_interval_hours), 2),
        "runtime_ratio": round(float(runtime_ratio), 4),
        "last_maintenance": equipment.last_maintenance.isoformat() if equipment.last_maintenance else None,
        "maintenance_overdue": maintenance_overdue,
        "risk_level": risk_level,
        "predicted_health_score": round(float(health_score), 2),
        "recommended_status": recommended_status,
    }


def build_operations_dashboard(warehouse_id: int | None = None) -> dict[str, Any]:
    queryset = Equipment.objects.select_related("warehouse").all()
    if warehouse_id is not None:
        queryset = queryset.filter(warehouse_id=warehouse_id)

    evaluations = [evaluate_equipment_health(equipment) for equipment in queryset]
    high_risk = [item for item in evaluations if item["risk_level"] == "high"]
    medium_risk = [item for item in evaluations if item["risk_level"] == "medium"]

    return {
        "warehouse_id": warehouse_id,
        "summary": {
            "equipment_count": len(evaluations),
            "high_risk_count": len(high_risk),
            "medium_risk_count": len(medium_risk),
            "healthy_count": len(evaluations) - len(high_risk) - len(medium_risk),
        },
        "alerts": high_risk + medium_risk,
        "equipments": evaluations,
    }