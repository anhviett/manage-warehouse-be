from django.db import models
from warehouse.models.base import AuditUserModel, TimeStampedModel
from warehouse.models.supplier import Supplier
from warehouse.models.warehouse import Warehouse


class ProductBatch(TimeStampedModel, AuditUserModel):
    product = models.ForeignKey("warehouse.Product", on_delete=models.CASCADE, related_name="batches")
    warehouse = models.ForeignKey("warehouse.Warehouse", on_delete=models.CASCADE, related_name="batches")
    batch_no = models.CharField(max_length=50)
    manufacturing_date = models.DateField(null=True, blank=True)
    expiry_date = models.DateField(null=True, blank=True)
    quantity = models.PositiveIntegerField(default=0)
    reserved_quantity = models.PositiveIntegerField(default=0)
    supplier = models.ForeignKey(
        "warehouse.Supplier",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="batches",
    )

    class Meta:
        ordering = ["expiry_date", "batch_no"]
        constraints = [
            models.UniqueConstraint(
                fields=["product", "warehouse", "batch_no"],
                name="uniq_product_batch_per_warehouse",
            )
        ]

    def __str__(self):
        return f"{self.product.sku} / {self.warehouse.code} / {self.batch_no}"