from django.db import models
from warehouse.models.base import AuditUserModel, TimeStampedModel
from django.core.validators import MinValueValidator



class GoodsReceiptItem(TimeStampedModel, AuditUserModel):
    goods_receipt = models.ForeignKey(
        "warehouse.GoodsReceipt",
        on_delete=models.CASCADE,
        related_name="items",
    )
    product = models.ForeignKey("warehouse.Product", on_delete=models.CASCADE, related_name="goods_receipt_items")
    batch = models.ForeignKey(
        "warehouse.ProductBatch",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="goods_receipt_items",
    )
    quantity = models.PositiveIntegerField(validators=[MinValueValidator(1)])
    unit_cost = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0,
        validators=[MinValueValidator(0)],
    )
    note = models.CharField(max_length=255, blank=True)

    class Meta:
        ordering = ["goods_receipt__receipt_no", "product__sku"]
        constraints = [
            models.UniqueConstraint(
                fields=["goods_receipt", "product", "batch"],
                name="uniq_goods_receipt_product_batch",
            )
        ]

    def __str__(self):
        return f"{self.goods_receipt.receipt_no} / {self.product.sku}"