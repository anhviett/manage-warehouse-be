from django.db import models
from warehouse.models.base import AuditUserModel, TimeStampedModel


class Inventory(TimeStampedModel, AuditUserModel):
    # Mỗi bản ghi biểu diễn tồn kho của 1 sản phẩm trong 1 kho cụ thể.
    warehouse = models.ForeignKey("warehouse.Warehouse", on_delete=models.CASCADE, related_name="inventories")
    product = models.ForeignKey("warehouse.Product", on_delete=models.CASCADE, related_name="inventories")
    quantity = models.PositiveIntegerField(default=0)
    reserved_quantity = models.PositiveIntegerField(default=0)
    damaged_quantity = models.PositiveIntegerField(default=0)
    reorder_level = models.PositiveIntegerField(default=0)
    safety_stock = models.PositiveIntegerField(default=0)
    max_stock_level = models.PositiveIntegerField(default=0)
    bin_location = models.CharField(max_length=100, blank=True)
    last_counted_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ["warehouse__code", "product__sku"]
        constraints = [
            models.UniqueConstraint(
                fields=["warehouse", "product"],
                name="uniq_inventory_warehouse_product",
            )
        ]

    def __str__(self):
        return f"{self.warehouse.code} / {self.product.sku}: {self.quantity}"

    @property
    def available_quantity(self):
        unavailable = self.reserved_quantity + self.damaged_quantity
        return max(self.quantity - unavailable, 0)