from django.conf import settings
from django.db import models
from warehouse.models.base import AuditUserModel, TimeStampedModel
from warehouse.models.warehouse import Warehouse


class StockTransfer(TimeStampedModel, AuditUserModel):
    STATUS_DRAFT = "DRAFT"
    STATUS_IN_TRANSIT = "IN_TRANSIT"
    STATUS_COMPLETED = "COMPLETED"
    STATUS_CANCELLED = "CANCELLED"

    STATUS_CHOICES = [
        (STATUS_DRAFT, "Draft"),
        (STATUS_IN_TRANSIT, "In Transit"),
        (STATUS_COMPLETED, "Completed"),
        (STATUS_CANCELLED, "Cancelled"),
    ]

    transfer_no = models.CharField(max_length=30, unique=True)
    source_warehouse = models.ForeignKey(
        Warehouse,
        on_delete=models.CASCADE,
        related_name="outgoing_transfers",
    )
    destination_warehouse = models.ForeignKey(
        Warehouse,
        on_delete=models.CASCADE,
        related_name="incoming_transfers",
    )
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_DRAFT)
    transferred_at = models.DateTimeField(null=True, blank=True)
    received_at = models.DateTimeField(null=True, blank=True)
    note = models.CharField(max_length=255, blank=True)
    approved_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="warehouse_stock_transfers_approved",
    )
    received_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="warehouse_stock_transfers_received",
    )

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return self.transfer_no
