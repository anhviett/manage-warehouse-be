from django.db import models
from warehouse.models.base import AuditUserModel, TimeStampedModel

class SerialNumber(TimeStampedModel, AuditUserModel):
    STATUS_IN_STOCK = "IN_STOCK"
    STATUS_RESERVED = "RESERVED"
    STATUS_SOLD = "SOLD"
    STATUS_DAMAGED = "DAMAGED"
    STATUS_RETURNED = "RETURNED"

    STATUS_CHOICES = [
        (STATUS_IN_STOCK, "In Stock"),
        (STATUS_RESERVED, "Reserved"),
        (STATUS_SOLD, "Sold"),
        (STATUS_DAMAGED, "Damaged"),
        (STATUS_RETURNED, "Returned"),
    ]

    product = models.ForeignKey("warehouse.Product", on_delete=models.CASCADE, related_name="serial_numbers")
    warehouse = models.ForeignKey("warehouse.Warehouse", on_delete=models.CASCADE, related_name="serial_numbers")
    batch = models.ForeignKey(
        "warehouse.ProductBatch",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="serial_numbers",
    )
    serial_number = models.CharField(max_length=100, unique=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_IN_STOCK)
    note = models.CharField(max_length=255, blank=True)

    class Meta:
        ordering = ["serial_number"]

    def __str__(self):
        return self.serial_number