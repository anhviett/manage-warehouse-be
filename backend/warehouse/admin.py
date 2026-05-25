from django.contrib import admin

from .models import (
    Category,
    GoodsIssue,
    GoodsIssueItem,
    GoodsReceipt,
    GoodsReceiptItem,
    Inventory,
    Product,
    ProductBatch,
    SerialNumber,
    StockCount,
    StockCountItem,
    StockMovement,
    StockTransfer,
    StockTransferItem,
    Supplier,
    Warehouse,
)


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "slug", "parent", "is_active", "created_by", "updated_at")
    search_fields = ("name", "slug")
    list_filter = ("is_active", "parent")


@admin.register(Supplier)
class SupplierAdmin(admin.ModelAdmin):
    list_display = ("code", "name", "contact_name", "phone", "is_active", "created_by", "updated_at")
    search_fields = ("code", "name", "contact_name", "phone", "email")
    list_filter = ("is_active",)


@admin.register(Warehouse)
class WarehouseAdmin(admin.ModelAdmin):
    list_display = ("code", "name", "manager_name", "is_active", "created_by", "updated_at")
    search_fields = ("code", "name", "manager_name")
    list_filter = ("is_active",)


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = (
        "sku",
        "name",
        "category",
        "supplier",
        "unit",
        "cost_price",
        "selling_price",
        "track_batch",
        "track_serial",
        "is_active",
        "created_by",
        "updated_at",
    )
    search_fields = ("sku", "name", "barcode", "brand")
    list_filter = ("is_active", "track_batch", "track_serial", "category", "supplier")


@admin.register(Inventory)
class InventoryAdmin(admin.ModelAdmin):
    list_display = (
        "warehouse",
        "product",
        "quantity",
        "reserved_quantity",
        "damaged_quantity",
        "reorder_level",
        "created_by",
        "updated_at",
    )
    search_fields = ("warehouse__code", "product__sku", "product__name")
    list_filter = ("warehouse",)


@admin.register(ProductBatch)
class ProductBatchAdmin(admin.ModelAdmin):
    list_display = (
        "product",
        "warehouse",
        "batch_no",
        "expiry_date",
        "quantity",
        "reserved_quantity",
        "created_by",
        "updated_at",
    )
    search_fields = ("product__sku", "product__name", "warehouse__code", "batch_no")
    list_filter = ("warehouse", "supplier", "expiry_date")


@admin.register(SerialNumber)
class SerialNumberAdmin(admin.ModelAdmin):
    list_display = (
        "serial_number",
        "product",
        "warehouse",
        "batch",
        "status",
        "created_by",
        "updated_at",
    )
    search_fields = ("serial_number", "product__sku", "product__name", "warehouse__code")
    list_filter = ("status", "warehouse", "product")


class GoodsReceiptItemInline(admin.TabularInline):
    model = GoodsReceiptItem
    extra = 0


@admin.register(GoodsReceipt)
class GoodsReceiptAdmin(admin.ModelAdmin):
    list_display = (
        "receipt_no",
        "warehouse",
        "supplier",
        "reference_no",
        "status",
        "received_at",
        "approved_by",
        "created_by",
        "updated_at",
    )
    search_fields = (
        "receipt_no",
        "reference_no",
        "warehouse__code",
        "warehouse__name",
        "supplier__code",
        "supplier__name",
    )
    list_filter = ("status", "warehouse", "supplier")
    inlines = [GoodsReceiptItemInline]


@admin.register(GoodsReceiptItem)
class GoodsReceiptItemAdmin(admin.ModelAdmin):
    list_display = ("goods_receipt", "product", "batch", "quantity", "unit_cost", "updated_at")
    search_fields = (
        "goods_receipt__receipt_no",
        "product__sku",
        "product__name",
        "batch__batch_no",
    )
    list_filter = ("goods_receipt",)


class GoodsIssueItemInline(admin.TabularInline):
    model = GoodsIssueItem
    extra = 0


@admin.register(GoodsIssue)
class GoodsIssueAdmin(admin.ModelAdmin):
    list_display = (
        "issue_no",
        "warehouse",
        "customer_name",
        "reference_no",
        "status",
        "issued_at",
        "approved_by",
        "created_by",
        "updated_at",
    )
    search_fields = (
        "issue_no",
        "reference_no",
        "customer_name",
        "warehouse__code",
        "warehouse__name",
    )
    list_filter = ("status", "warehouse")
    inlines = [GoodsIssueItemInline]


@admin.register(GoodsIssueItem)
class GoodsIssueItemAdmin(admin.ModelAdmin):
    list_display = ("goods_issue", "product", "batch", "quantity", "unit_price", "updated_at")
    search_fields = (
        "goods_issue__issue_no",
        "product__sku",
        "product__name",
        "batch__batch_no",
    )
    list_filter = ("goods_issue",)


@admin.register(StockMovement)
class StockMovementAdmin(admin.ModelAdmin):
    list_display = (
        "warehouse",
        "product",
        "batch",
        "serial_number",
        "goods_receipt",
        "goods_issue",
        "stock_transfer",
        "stock_count",
        "movement_type",
        "quantity",
        "reason_code",
        "movement_at",
    )
    search_fields = (
        "warehouse__code",
        "product__sku",
        "product__name",
        "reference_no",
        "note",
    )
    list_filter = ("movement_type", "reason_code", "warehouse")


class StockTransferItemInline(admin.TabularInline):
    model = StockTransferItem
    extra = 0


@admin.register(StockTransfer)
class StockTransferAdmin(admin.ModelAdmin):
    list_display = (
        "transfer_no",
        "source_warehouse",
        "destination_warehouse",
        "status",
        "transferred_at",
        "received_at",
        "approved_by",
        "received_by",
        "created_by",
        "updated_at",
    )
    search_fields = ("transfer_no", "source_warehouse__code", "destination_warehouse__code")
    list_filter = ("status", "source_warehouse", "destination_warehouse")
    inlines = [StockTransferItemInline]


@admin.register(StockTransferItem)
class StockTransferItemAdmin(admin.ModelAdmin):
    list_display = ("transfer", "product", "batch", "quantity", "updated_at")
    search_fields = ("transfer__transfer_no", "product__sku", "product__name", "batch__batch_no")
    list_filter = ("transfer",)


class StockCountItemInline(admin.TabularInline):
    model = StockCountItem
    extra = 0


@admin.register(StockCount)
class StockCountAdmin(admin.ModelAdmin):
    list_display = (
        "count_no",
        "warehouse",
        "status",
        "counted_at",
        "counted_by",
        "approved_by",
        "created_by",
        "updated_at",
    )
    search_fields = ("count_no", "warehouse__code", "warehouse__name")
    list_filter = ("status", "warehouse")
    inlines = [StockCountItemInline]


@admin.register(StockCountItem)
class StockCountItemAdmin(admin.ModelAdmin):
    list_display = (
        "stock_count",
        "product",
        "batch",
        "expected_quantity",
        "counted_quantity",
        "difference_quantity",
        "updated_at",
    )
    search_fields = (
        "stock_count__count_no",
        "product__sku",
        "product__name",
        "batch__batch_no",
    )
    list_filter = ("stock_count",)