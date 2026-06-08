from django.db import models
from django.conf import settings
from warehouse.models.base import AuditUserModel, TimeStampedModel
from warehouse.models.supplier import Supplier
from warehouse.models.warehouse import Warehouse




class GoodsReceipt(TimeStampedModel, AuditUserModel):
    STATUS_DRAFT = "DRAFT"
    STATUS_POSTED = "POSTED"
    STATUS_CANCELLED = "CANCELLED"

    STATUS_CHOICES = [
        (STATUS_DRAFT, "Draft"),
        (STATUS_POSTED, "Posted"),
        (STATUS_CANCELLED, "Cancelled"),
    ]

    receipt_no = models.CharField(max_length=30, unique=True)
    warehouse = models.ForeignKey(Warehouse, on_delete=models.CASCADE, related_name="goods_receipts")
    supplier = models.ForeignKey(
        Supplier,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="goods_receipts",
    )
    reference_no = models.CharField(max_length=50, blank=True)
    received_at = models.DateTimeField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_DRAFT)
    note = models.CharField(max_length=255, blank=True)
    approved_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="warehouse_goods_receipts_approved",
    )

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return self.receipt_no