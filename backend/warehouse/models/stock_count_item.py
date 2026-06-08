

from django.db import models
from warehouse.models.base import AuditUserModel, TimeStampedModel


class StockCountItem(TimeStampedModel, AuditUserModel):
    stock_count = models.ForeignKey(
        "warehouse.StockCount",
        on_delete=models.CASCADE,
        related_name="items",
    )
    product = models.ForeignKey("warehouse.Product", on_delete=models.CASCADE, related_name="stock_count_items")
    batch = models.ForeignKey(
        "warehouse.ProductBatch",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="stock_count_items",
    )
    expected_quantity = models.PositiveIntegerField(default=0)
    counted_quantity = models.PositiveIntegerField(default=0)
    difference_quantity = models.IntegerField(default=0)
    note = models.CharField(max_length=255, blank=True)

    class Meta:
        ordering = ["stock_count__count_no", "product__sku"]
        constraints = [
            models.UniqueConstraint(
                fields=["stock_count", "product", "batch"],
                name="uniq_stock_count_product_batch",
            )
        ]

    def __str__(self):
        return f"{self.stock_count.count_no} / {self.product.sku}"