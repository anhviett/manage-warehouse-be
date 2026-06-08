from warehouse.models.base import AuditUserModel, TimeStampedModel
from django.db import models

class Warehouse(TimeStampedModel, AuditUserModel):
    # Mã kho là duy nhất để tham chiếu nhanh trong API/report.
    code = models.CharField(max_length=20, unique=True)
    name = models.CharField(max_length=100)
    address = models.CharField(max_length=255, blank=True)
    manager_name = models.CharField(max_length=100, blank=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ["code"]

    def __str__(self):
        return f"{self.code} - {self.name}"