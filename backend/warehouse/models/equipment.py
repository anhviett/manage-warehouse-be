from django.db import models
from django.core.validators import MinValueValidator

from warehouse.models.base import AuditUserModel, TimeStampedModel
from warehouse.models.warehouse import Warehouse

class Equipment(TimeStampedModel, AuditUserModel):
    STATUS_OPERATIONAL = "OPERATIONAL"
    STATUS_MAINTENANCE = "MAINTENANCE"
    STATUS_WARNING = "WARNING"
    STATUS_INACTIVE = "INACTIVE"

    STATUS_CHOICES = [
        (STATUS_OPERATIONAL, "Operational"),
        (STATUS_MAINTENANCE, "Maintenance"),
        (STATUS_WARNING, "Warning"),
        (STATUS_INACTIVE, "Inactive"),
    ]

    warehouse = models.ForeignKey(
        Warehouse,
        on_delete=models.CASCADE,
        related_name="equipments",
    )
    name = models.CharField(max_length=100)
    code = models.CharField(max_length=50)
    equipment_type = models.CharField(max_length=50, blank=True)
    last_maintenance = models.DateTimeField(null=True, blank=True)
    runtime_hours = models.FloatField(default=0, validators=[MinValueValidator(0)])
    health_score = models.FloatField(default=100, validators=[MinValueValidator(0)])
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default=STATUS_OPERATIONAL,
    )
    maintenance_interval_hours = models.FloatField(
        default=1000,
        validators=[MinValueValidator(1)],
    )
    note = models.CharField(max_length=255, blank=True)

    class Meta:
        ordering = ["warehouse__code", "code"]
        constraints = [
            models.UniqueConstraint(
                fields=["warehouse", "code"],
                name="uniq_equipment_code_per_warehouse",
            )
        ]

    def __str__(self):
        return f"{self.warehouse.code} / {self.code}"