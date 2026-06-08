
from django.core.validators import MinValueValidator
from django.db import models
from warehouse.models.base import AuditUserModel, TimeStampedModel


class StockMovement(TimeStampedModel, AuditUserModel):
    # Loại nghiệp vụ kho:
    # - IN: nhập kho (tăng tồn)
    # - OUT: xuất kho (giảm tồn)
    # - ADJUST: kiểm kho/điều chỉnh tồn về số lượng mục tiêu
    MOVEMENT_IN = "IN"
    MOVEMENT_OUT = "OUT"
    MOVEMENT_ADJUST = "ADJUST"

    MOVEMENT_CHOICES = [
        (MOVEMENT_IN, "Stock In"),
        (MOVEMENT_OUT, "Stock Out"),
        (MOVEMENT_ADJUST, "Adjustment"),
    ]

    REASON_PURCHASE = "PURCHASE"
    REASON_SALE = "SALE"
    REASON_RETURN = "RETURN"
    REASON_DAMAGE = "DAMAGE"
    REASON_STOCK_COUNT = "STOCK_COUNT"
    REASON_TRANSFER = "TRANSFER"
    REASON_INITIAL = "INITIAL"
    REASON_MANUAL = "MANUAL"

    REASON_CHOICES = [
        (REASON_PURCHASE, "Purchase"),
        (REASON_SALE, "Sale"),
        (REASON_RETURN, "Return"),
        (REASON_DAMAGE, "Damage"),
        (REASON_STOCK_COUNT, "Stock Count"),
        (REASON_TRANSFER, "Transfer"),
        (REASON_INITIAL, "Initial Balance"),
        (REASON_MANUAL, "Manual"),
    ]

    warehouse = models.ForeignKey("warehouse.Warehouse", on_delete=models.CASCADE, related_name="stock_movements")
    product = models.ForeignKey("warehouse.Product", on_delete=models.CASCADE, related_name="stock_movements")
    batch = models.ForeignKey(
        "warehouse.ProductBatch",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="stock_movements",
    )
    serial_number = models.ForeignKey(
        "warehouse.SerialNumber",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="stock_movements",
    )
    goods_receipt = models.ForeignKey(
        "warehouse.GoodsReceipt",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="stock_movements",
    )
    goods_issue = models.ForeignKey(
        "warehouse.GoodsIssue",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="stock_movements",
    )
    stock_transfer = models.ForeignKey(
        "warehouse.StockTransfer",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="stock_movements",
    )
    stock_count = models.ForeignKey(
        "warehouse.StockCount",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="stock_movements",
    )
    movement_type = models.CharField(max_length=10, choices=MOVEMENT_CHOICES)
    # quantity là số lượng nghiệp vụ:
    # - IN / OUT: số lượng tăng/giảm
    # - ADJUST: số lượng tồn mục tiêu sau điều chỉnh
    quantity = models.PositiveIntegerField(validators=[MinValueValidator(0)])
    movement_at = models.DateTimeField(auto_now_add=True)
    reference_no = models.CharField(max_length=50, blank=True)
    reason_code = models.CharField(max_length=20, choices=REASON_CHOICES, default=REASON_MANUAL)
    quantity_before = models.PositiveIntegerField(default=0)
    quantity_after = models.PositiveIntegerField(default=0)
    note = models.CharField(max_length=255, blank=True)

    class Meta:
        ordering = ["-movement_at", "-created_at"]

    def __str__(self):
        return f"{self.movement_type} - {self.product.sku} - {self.quantity}"