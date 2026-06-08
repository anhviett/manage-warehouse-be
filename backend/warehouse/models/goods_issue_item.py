
from warehouse.models.base import AuditUserModel, TimeStampedModel
from django.db import models
from django.core.validators import MinValueValidator

class GoodsIssueItem(TimeStampedModel, AuditUserModel):
    goods_issue = models.ForeignKey(
        "warehouse.GoodsIssue",
        on_delete=models.CASCADE,
        related_name="items",
    )
    product = models.ForeignKey("warehouse.Product", on_delete=models.CASCADE, related_name="goods_issue_items")
    batch = models.ForeignKey(
        "warehouse.ProductBatch",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="goods_issue_items",
    )
    quantity = models.PositiveIntegerField(validators=[MinValueValidator(1)])
    unit_price = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0,
        validators=[MinValueValidator(0)],
    )
    note = models.CharField(max_length=255, blank=True)

    class Meta:
        ordering = ["goods_issue__issue_no", "product__sku"]
        constraints = [
            models.UniqueConstraint(
                fields=["goods_issue", "product", "batch"],
                name="uniq_goods_issue_product_batch",
            )
        ]

    def __str__(self):
        return f"{self.goods_issue.issue_no} / {self.product.sku}"