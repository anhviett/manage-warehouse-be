from django.conf import settings
from django.core.validators import MinValueValidator
from django.db import models


# Base model dùng để tự động lưu thời gian tạo/cập nhật cho tất cả bảng kế thừa.
class TimeStampedModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class AuditUserModel(models.Model):
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="%(app_label)s_%(class)s_created",
    )
    updated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="%(app_label)s_%(class)s_updated",
    )

    class Meta:
        abstract = True


class Category(TimeStampedModel, AuditUserModel):
    # Danh mục sản phẩm, hỗ trợ cây cha-con để nhóm hàng hóa.
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=100, unique=True)
    parent = models.ForeignKey(
        "self",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="children",
    )
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ["name"]
        verbose_name_plural = "categories"

    def __str__(self):
        return self.name


class Supplier(TimeStampedModel, AuditUserModel):
    code = models.CharField(max_length=20, unique=True)
    name = models.CharField(max_length=150)
    contact_name = models.CharField(max_length=100, blank=True)
    phone = models.CharField(max_length=30, blank=True)
    email = models.EmailField(blank=True)
    address = models.CharField(max_length=255, blank=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ["code"]

    def __str__(self):
        return f"{self.code} - {self.name}"


class Warehouse(TimeStampedModel, AuditUserModel):
    # Mã kho là duy nhất để tham chiếu nhanh trong API/report.
    code = models.CharField(max_length=20, unique=True)
    name = models.CharField(max_length=100)
    address = models.CharField(max_length=255, blank=True)
    manager_name = models.CharField(max_length=100, blank=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ["code"]

    def __str__(self):
        return f"{self.code} - {self.name}"


class Product(TimeStampedModel, AuditUserModel):
    # SKU là mã định danh duy nhất của sản phẩm.
    sku = models.CharField(max_length=30, unique=True)
    name = models.CharField(max_length=150)
    barcode = models.CharField(max_length=50, blank=True)
    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="products",
    )
    supplier = models.ForeignKey(
        Supplier,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="products",
    )
    brand = models.CharField(max_length=100, blank=True)
    description = models.TextField(blank=True)
    unit = models.CharField(max_length=20, default="pcs")
    cost_price = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0,
        validators=[MinValueValidator(0)],
    )
    selling_price = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0,
        validators=[MinValueValidator(0)],
    )
    track_batch = models.BooleanField(default=False)
    track_serial = models.BooleanField(default=False)
    shelf_life_days = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ["sku"]

    def __str__(self):
        return f"{self.sku} - {self.name}"


class Inventory(TimeStampedModel, AuditUserModel):
    # Mỗi bản ghi biểu diễn tồn kho của 1 sản phẩm trong 1 kho cụ thể.
    warehouse = models.ForeignKey(Warehouse, on_delete=models.CASCADE, related_name="inventories")
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="inventories")
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


class ProductBatch(TimeStampedModel, AuditUserModel):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="batches")
    warehouse = models.ForeignKey(Warehouse, on_delete=models.CASCADE, related_name="batches")
    batch_no = models.CharField(max_length=50)
    manufacturing_date = models.DateField(null=True, blank=True)
    expiry_date = models.DateField(null=True, blank=True)
    quantity = models.PositiveIntegerField(default=0)
    reserved_quantity = models.PositiveIntegerField(default=0)
    supplier = models.ForeignKey(
        Supplier,
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

    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="serial_numbers")
    warehouse = models.ForeignKey(Warehouse, on_delete=models.CASCADE, related_name="serial_numbers")
    batch = models.ForeignKey(
        ProductBatch,
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


class GoodsReceiptItem(TimeStampedModel, AuditUserModel):
    goods_receipt = models.ForeignKey(
        GoodsReceipt,
        on_delete=models.CASCADE,
        related_name="items",
    )
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="goods_receipt_items")
    batch = models.ForeignKey(
        ProductBatch,
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


class GoodsIssue(TimeStampedModel, AuditUserModel):
    STATUS_DRAFT = "DRAFT"
    STATUS_POSTED = "POSTED"
    STATUS_CANCELLED = "CANCELLED"

    STATUS_CHOICES = [
        (STATUS_DRAFT, "Draft"),
        (STATUS_POSTED, "Posted"),
        (STATUS_CANCELLED, "Cancelled"),
    ]

    issue_no = models.CharField(max_length=30, unique=True)
    warehouse = models.ForeignKey(Warehouse, on_delete=models.CASCADE, related_name="goods_issues")
    customer_name = models.CharField(max_length=150, blank=True)
    reference_no = models.CharField(max_length=50, blank=True)
    issued_at = models.DateTimeField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_DRAFT)
    note = models.CharField(max_length=255, blank=True)
    approved_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="warehouse_goods_issues_approved",
    )

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return self.issue_no


class GoodsIssueItem(TimeStampedModel, AuditUserModel):
    goods_issue = models.ForeignKey(
        GoodsIssue,
        on_delete=models.CASCADE,
        related_name="items",
    )
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="goods_issue_items")
    batch = models.ForeignKey(
        ProductBatch,
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

    warehouse = models.ForeignKey(Warehouse, on_delete=models.CASCADE, related_name="stock_movements")
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="stock_movements")
    batch = models.ForeignKey(
        ProductBatch,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="stock_movements",
    )
    serial_number = models.ForeignKey(
        SerialNumber,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="stock_movements",
    )
    goods_receipt = models.ForeignKey(
        GoodsReceipt,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="stock_movements",
    )
    goods_issue = models.ForeignKey(
        GoodsIssue,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="stock_movements",
    )
    stock_transfer = models.ForeignKey(
        "StockTransfer",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="stock_movements",
    )
    stock_count = models.ForeignKey(
        "StockCount",
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


class StockTransferItem(TimeStampedModel, AuditUserModel):
    transfer = models.ForeignKey(
        StockTransfer,
        on_delete=models.CASCADE,
        related_name="items",
    )
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="transfer_items")
    batch = models.ForeignKey(
        ProductBatch,
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


class StockCount(TimeStampedModel, AuditUserModel):
    STATUS_DRAFT = "DRAFT"
    STATUS_POSTED = "POSTED"
    STATUS_CANCELLED = "CANCELLED"

    STATUS_CHOICES = [
        (STATUS_DRAFT, "Draft"),
        (STATUS_POSTED, "Posted"),
        (STATUS_CANCELLED, "Cancelled"),
    ]

    count_no = models.CharField(max_length=30, unique=True)
    warehouse = models.ForeignKey(Warehouse, on_delete=models.CASCADE, related_name="stock_counts")
    counted_at = models.DateTimeField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_DRAFT)
    note = models.CharField(max_length=255, blank=True)
    counted_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="warehouse_stock_counts_counted",
    )
    approved_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="warehouse_stock_counts_approved",
    )

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return self.count_no


class StockCountItem(TimeStampedModel, AuditUserModel):
    stock_count = models.ForeignKey(
        StockCount,
        on_delete=models.CASCADE,
        related_name="items",
    )
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="stock_count_items")
    batch = models.ForeignKey(
        ProductBatch,
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