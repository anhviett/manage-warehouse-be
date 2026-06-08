from django.core.validators import MinValueValidator
from django.db import models
from warehouse.models.base import AuditUserModel, TimeStampedModel


class StockTransferItem(TimeStampedModel, AuditUserModel):
    transfer = models.ForeignKey(
        "warehouse.StockTransfer",
        on_delete=models.CASCADE,
        related_name="items",
    )
    product = models.ForeignKey("warehouse.Product", on_delete=models.CASCADE, related_name="transfer_items")
    batch = models.ForeignKey(
        "warehouse.ProductBatch",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="transfer_items",
    )
    quantity = models.PositiveIntegerField(validators=[MinValueValidator(1)])

    class Meta:
        ordering = ["transfer__transfer_no", "product__sku"]
        constraints = [
            models.UniqueConstraint(
                fields=["transfer", "product", "batch"],
                name="uniq_transfer_product_batch",
            )
        ]

    def __str__(self):
        return f"{self.transfer.transfer_no} / {self.product.sku}"
