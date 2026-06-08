import logging

from rest_framework import serializers

logger = logging.getLogger(__name__)

from .fields import (
    CategoryFields,
    GoodsIssueFields,
    GoodsIssueItemFields,
    GoodsReceiptFields,
    GoodsReceiptItemFields,
    InventoryFields,
    ProductBatchFields,
    ProductFields,
    SerialNumberFields,
    StockCountFields,
    StockCountItemFields,
    StockMovementFields,
    StockTransferFields,
    StockTransferItemFields,
    SupplierFields,
    WarehouseFields,
)
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

# Serializer trong DRF tương đương DTO + validation layer cho request/response.
# Docs:
# - DRF Serializers: https://www.django-rest-framework.org/api-guide/serializers/
# - DRF Validation: https://www.django-rest-framework.org/api-guide/serializers/#validation


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = [
            CategoryFields.ID,
            CategoryFields.NAME,
            CategoryFields.SLUG,
            CategoryFields.PARENT,
            CategoryFields.DESCRIPTION,
            CategoryFields.IS_ACTIVE,
            CategoryFields.CREATED_BY,
            CategoryFields.UPDATED_BY,
            CategoryFields.CREATED_AT,
            CategoryFields.UPDATED_AT,
        ]
        read_only_fields = [
            CategoryFields.ID,
            CategoryFields.CREATED_AT,
            CategoryFields.UPDATED_AT,
        ]


class SupplierSerializer(serializers.ModelSerializer):
    class Meta:
        model = Supplier
        fields = [
            SupplierFields.ID,
            SupplierFields.CODE,
            SupplierFields.NAME,
            SupplierFields.CONTACT_NAME,
            SupplierFields.PHONE,
            SupplierFields.EMAIL,
            SupplierFields.ADDRESS,
            SupplierFields.IS_ACTIVE,
            SupplierFields.CREATED_BY,
            SupplierFields.UPDATED_BY,
            SupplierFields.CREATED_AT,
            SupplierFields.UPDATED_AT,
        ]
        read_only_fields = [
            SupplierFields.ID,
            SupplierFields.CREATED_AT,
            SupplierFields.UPDATED_AT,
        ]


class WarehouseSerializer(serializers.ModelSerializer):
    created_at = serializers.DateTimeField(format="%d/%m/%Y %H:%M:%S", read_only=True)
    class Meta:
        model = Warehouse
        fields = [
            WarehouseFields.ID,
            WarehouseFields.CODE,
            WarehouseFields.NAME,
            WarehouseFields.ADDRESS,
            WarehouseFields.MANAGER_NAME,
            WarehouseFields.IS_ACTIVE,
            WarehouseFields.CREATED_BY,
            WarehouseFields.UPDATED_BY,
            WarehouseFields.CREATED_AT,
            WarehouseFields.UPDATED_AT,
        ]
        read_only_fields = [
            WarehouseFields.ID,
            WarehouseFields.CREATED_AT,
            WarehouseFields.UPDATED_AT,
        ]


class ProductSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(source="category.name", read_only=True)
    supplier_name = serializers.CharField(source="supplier.name", read_only=True)
    supplier_code = serializers.CharField(source="supplier.code", read_only=True)
    supplier_phone = serializers.CharField(source="supplier.phone", read_only=True)
    supplier_address = serializers.CharField(source="supplier.address", read_only=True)
    supplier_status = serializers.CharField(source="supplier.is_active", read_only=True)
    qr_payload = serializers.SerializerMethodField()
    qr_label = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = [
            ProductFields.ID,
            ProductFields.SKU,
            ProductFields.NAME,
            ProductFields.BARCODE,
            ProductFields.CATEGORY,
            ProductFields.CATEGORY_NAME,
            ProductFields.SUPPLIER,
            ProductFields.SUPPLIER_NAME,
            ProductFields.SUPPLIER_CODE,
            ProductFields.SUPPLIER_PHONE,
            ProductFields.SUPPLIER_ADDRESS,
            ProductFields.SUPPLIER_STATUS,
            ProductFields.BRAND,
            ProductFields.DESCRIPTION,
            ProductFields.UNIT,
            ProductFields.COST_PRICE,
            ProductFields.SELLING_PRICE,
            ProductFields.TRACK_BATCH,
            ProductFields.TRACK_SERIAL,
            ProductFields.SHELF_LIFE_DAYS,
            ProductFields.IS_ACTIVE,
            ProductFields.QR_PAYLOAD,
            ProductFields.QR_LABEL,
            ProductFields.CREATED_BY,
            ProductFields.UPDATED_BY,
            ProductFields.CREATED_AT,
            ProductFields.UPDATED_AT,
        ]
        read_only_fields = [
            ProductFields.ID,
            ProductFields.CATEGORY_NAME,
            ProductFields.SUPPLIER_NAME,
            ProductFields.SUPPLIER_CODE,
            ProductFields.SUPPLIER_PHONE,
            ProductFields.SUPPLIER_ADDRESS,
            ProductFields.SUPPLIER_STATUS,
            ProductFields.QR_PAYLOAD,
            ProductFields.QR_LABEL,
            ProductFields.CREATED_AT,
            ProductFields.UPDATED_AT,
        ]

    def get_qr_payload(self, obj):
        logger.warning(
            "Product QR payload serializer=%s obj=%s product_id=%s sku=%s barcode=%s context=%s",
            self.__class__.__name__,
            obj.__class__.__name__,
            obj.id,
            obj.sku,
            obj.barcode,
            getattr(self, "context", {}),
        )
        return {
            "type": "product",
            "product_id": obj.id,
            "sku": obj.sku,
            "name": obj.name,
            "barcode": obj.barcode,
            "unit": obj.unit,
            "category_name": obj.category.name if obj.category else None,
            "supplier_code": obj.supplier.code if obj.supplier else None,
            "track_batch": obj.track_batch,
            "track_serial": obj.track_serial,
            "is_active": obj.is_active,
        }

    def get_qr_label(self, obj):
        return f"PRODUCT:{obj.sku}"


class InventorySerializer(serializers.ModelSerializer):
    warehouse_code = serializers.CharField(source="warehouse.code", read_only=True)
    warehouse_name = serializers.CharField(source="warehouse.name", read_only=True)
    product_sku = serializers.CharField(source="product.sku", read_only=True)
    product_name = serializers.CharField(source="product.name", read_only=True)
    product_unit = serializers.CharField(source="product.unit", read_only=True)
    available_quantity = serializers.IntegerField(read_only=True)
    is_below_reorder_level = serializers.SerializerMethodField()
    qr_payload = serializers.SerializerMethodField()
    qr_label = serializers.SerializerMethodField()

    class Meta:
        model = Inventory
        fields = [
            InventoryFields.ID,
            InventoryFields.WAREHOUSE,
            InventoryFields.WAREHOUSE_CODE,
            InventoryFields.WAREHOUSE_NAME,
            InventoryFields.PRODUCT,
            InventoryFields.PRODUCT_SKU,
            InventoryFields.PRODUCT_NAME,
            InventoryFields.PRODUCT_UNIT,
            InventoryFields.QUANTITY,
            InventoryFields.RESERVED_QUANTITY,
            InventoryFields.DAMAGED_QUANTITY,
            InventoryFields.AVAILABLE_QUANTITY,
            InventoryFields.REORDER_LEVEL,
            InventoryFields.SAFETY_STOCK,
            InventoryFields.MAX_STOCK_LEVEL,
            InventoryFields.BIN_LOCATION,
            InventoryFields.LAST_COUNTED_AT,
            InventoryFields.IS_BELOW_REORDER_LEVEL,
            InventoryFields.QR_PAYLOAD,
            InventoryFields.QR_LABEL,
            InventoryFields.CREATED_BY,
            InventoryFields.UPDATED_BY,
            InventoryFields.CREATED_AT,
            InventoryFields.UPDATED_AT,
        ]
        read_only_fields = [
            InventoryFields.ID,
            InventoryFields.WAREHOUSE_CODE,
            InventoryFields.WAREHOUSE_NAME,
            InventoryFields.PRODUCT_SKU,
            InventoryFields.PRODUCT_NAME,
            InventoryFields.PRODUCT_UNIT,
            InventoryFields.AVAILABLE_QUANTITY,
            InventoryFields.IS_BELOW_REORDER_LEVEL,
            InventoryFields.QR_PAYLOAD,
            InventoryFields.QR_LABEL,
            InventoryFields.CREATED_AT,
            InventoryFields.UPDATED_AT,
        ]

    def get_is_below_reorder_level(self, obj):
        return obj.available_quantity <= obj.reorder_level

    def get_qr_payload(self, obj):
        logger.warning(
            "Inventory QR payload serializer=%s obj=%s inventory_id=%s warehouse_id=%s product_id=%s sku=%s context=%s",
            self.__class__.__name__,
            obj.__class__.__name__,
            obj.id,
            obj.warehouse_id,
            obj.product_id,
            obj.product.sku,
            getattr(self, "context", {}),
        )
        return {
            "type": "inventory",
            "inventory_id": obj.id,
            "warehouse_id": obj.warehouse_id,
            "warehouse_code": obj.warehouse.code,
            "warehouse_name": obj.warehouse.name,
            "product_id": obj.product_id,
            "sku": obj.product.sku,
            "product_name": obj.product.name,
            "product_unit": obj.product.unit,
            "quantity": obj.quantity,
            "available_quantity": obj.available_quantity,
            "reserved_quantity": obj.reserved_quantity,
            "damaged_quantity": obj.damaged_quantity,
            "reorder_level": obj.reorder_level,
            "bin_location": obj.bin_location,
            "is_below_reorder_level": obj.available_quantity <= obj.reorder_level,
        }

    def get_qr_label(self, obj):
        return f"INV:{obj.warehouse.code}:{obj.product.sku}"


class ProductBatchSerializer(serializers.ModelSerializer):
    product_sku = serializers.CharField(source="product.sku", read_only=True)
    warehouse_code = serializers.CharField(source="warehouse.code", read_only=True)
    supplier_name = serializers.CharField(source="supplier.name", read_only=True)

    class Meta:
        model = ProductBatch
        fields = [
            ProductBatchFields.ID,
            ProductBatchFields.PRODUCT,
            ProductBatchFields.PRODUCT_SKU,
            ProductBatchFields.WAREHOUSE,
            ProductBatchFields.WAREHOUSE_CODE,
            ProductBatchFields.BATCH_NO,
            ProductBatchFields.MANUFACTURING_DATE,
            ProductBatchFields.EXPIRY_DATE,
            ProductBatchFields.QUANTITY,
            ProductBatchFields.RESERVED_QUANTITY,
            ProductBatchFields.SUPPLIER,
            ProductBatchFields.SUPPLIER_NAME,
            ProductBatchFields.CREATED_BY,
            ProductBatchFields.UPDATED_BY,
            ProductBatchFields.CREATED_AT,
            ProductBatchFields.UPDATED_AT,
        ]
        read_only_fields = [
            ProductBatchFields.ID,
            ProductBatchFields.PRODUCT_SKU,
            ProductBatchFields.WAREHOUSE_CODE,
            ProductBatchFields.SUPPLIER_NAME,
            ProductBatchFields.CREATED_AT,
            ProductBatchFields.UPDATED_AT,
        ]


class SerialNumberSerializer(serializers.ModelSerializer):
    product_sku = serializers.CharField(source="product.sku", read_only=True)
    warehouse_code = serializers.CharField(source="warehouse.code", read_only=True)
    batch_no = serializers.CharField(source="batch.batch_no", read_only=True)

    class Meta:
        model = SerialNumber
        fields = [
            SerialNumberFields.ID,
            SerialNumberFields.PRODUCT,
            SerialNumberFields.PRODUCT_SKU,
            SerialNumberFields.WAREHOUSE,
            SerialNumberFields.WAREHOUSE_CODE,
            SerialNumberFields.BATCH,
            SerialNumberFields.BATCH_NO,
            SerialNumberFields.SERIAL_NUMBER,
            SerialNumberFields.STATUS,
            SerialNumberFields.NOTE,
            SerialNumberFields.CREATED_BY,
            SerialNumberFields.UPDATED_BY,
            SerialNumberFields.CREATED_AT,
            SerialNumberFields.UPDATED_AT,
        ]
        read_only_fields = [
            SerialNumberFields.ID,
            SerialNumberFields.PRODUCT_SKU,
            SerialNumberFields.WAREHOUSE_CODE,
            SerialNumberFields.BATCH_NO,
            SerialNumberFields.CREATED_AT,
            SerialNumberFields.UPDATED_AT,
        ]


class GoodsReceiptSerializer(serializers.ModelSerializer):
    warehouse_code = serializers.CharField(source="warehouse.code", read_only=True)
    supplier_name = serializers.CharField(source="supplier.name", read_only=True)

    class Meta:
        model = GoodsReceipt
        fields = [
            GoodsReceiptFields.ID,
            GoodsReceiptFields.RECEIPT_NO,
            GoodsReceiptFields.WAREHOUSE,
            GoodsReceiptFields.WAREHOUSE_CODE,
            GoodsReceiptFields.SUPPLIER,
            GoodsReceiptFields.SUPPLIER_NAME,
            GoodsReceiptFields.REFERENCE_NO,
            GoodsReceiptFields.RECEIVED_AT,
            GoodsReceiptFields.STATUS,
            GoodsReceiptFields.NOTE,
            GoodsReceiptFields.APPROVED_BY,
            GoodsReceiptFields.CREATED_BY,
            GoodsReceiptFields.UPDATED_BY,
            GoodsReceiptFields.CREATED_AT,
            GoodsReceiptFields.UPDATED_AT,
        ]
        read_only_fields = [
            GoodsReceiptFields.ID,
            GoodsReceiptFields.WAREHOUSE_CODE,
            GoodsReceiptFields.SUPPLIER_NAME,
            GoodsReceiptFields.CREATED_AT,
            GoodsReceiptFields.UPDATED_AT,
        ]


class GoodsReceiptItemSerializer(serializers.ModelSerializer):
    receipt_no = serializers.CharField(source="goods_receipt.receipt_no", read_only=True)
    product_sku = serializers.CharField(source="product.sku", read_only=True)
    batch_no = serializers.CharField(source="batch.batch_no", read_only=True)

    class Meta:
        model = GoodsReceiptItem
        fields = [
            GoodsReceiptItemFields.ID,
            GoodsReceiptItemFields.GOODS_RECEIPT,
            GoodsReceiptItemFields.RECEIPT_NO,
            GoodsReceiptItemFields.PRODUCT,
            GoodsReceiptItemFields.PRODUCT_SKU,
            GoodsReceiptItemFields.BATCH,
            GoodsReceiptItemFields.BATCH_NO,
            GoodsReceiptItemFields.QUANTITY,
            GoodsReceiptItemFields.UNIT_COST,
            GoodsReceiptItemFields.NOTE,
            GoodsReceiptItemFields.CREATED_BY,
            GoodsReceiptItemFields.UPDATED_BY,
            GoodsReceiptItemFields.CREATED_AT,
            GoodsReceiptItemFields.UPDATED_AT,
        ]
        read_only_fields = [
            GoodsReceiptItemFields.ID,
            GoodsReceiptItemFields.RECEIPT_NO,
            GoodsReceiptItemFields.PRODUCT_SKU,
            GoodsReceiptItemFields.BATCH_NO,
            GoodsReceiptItemFields.CREATED_AT,
            GoodsReceiptItemFields.UPDATED_AT,
        ]


class GoodsIssueSerializer(serializers.ModelSerializer):
    warehouse_code = serializers.CharField(source="warehouse.code", read_only=True)

    class Meta:
        model = GoodsIssue
        fields = [
            GoodsIssueFields.ID,
            GoodsIssueFields.ISSUE_NO,
            GoodsIssueFields.WAREHOUSE,
            GoodsIssueFields.WAREHOUSE_CODE,
            GoodsIssueFields.CUSTOMER_NAME,
            GoodsIssueFields.REFERENCE_NO,
            GoodsIssueFields.ISSUED_AT,
            GoodsIssueFields.STATUS,
            GoodsIssueFields.NOTE,
            GoodsIssueFields.APPROVED_BY,
            GoodsIssueFields.CREATED_BY,
            GoodsIssueFields.UPDATED_BY,
            GoodsIssueFields.CREATED_AT,
            GoodsIssueFields.UPDATED_AT,
        ]
        read_only_fields = [
            GoodsIssueFields.ID,
            GoodsIssueFields.WAREHOUSE_CODE,
            GoodsIssueFields.CREATED_AT,
            GoodsIssueFields.UPDATED_AT,
        ]


class GoodsIssueItemSerializer(serializers.ModelSerializer):
    issue_no = serializers.CharField(source="goods_issue.issue_no", read_only=True)
    product_sku = serializers.CharField(source="product.sku", read_only=True)
    batch_no = serializers.CharField(source="batch.batch_no", read_only=True)

    class Meta:
        model = GoodsIssueItem
        fields = [
            GoodsIssueItemFields.ID,
            GoodsIssueItemFields.GOODS_ISSUE,
            GoodsIssueItemFields.ISSUE_NO,
            GoodsIssueItemFields.PRODUCT,
            GoodsIssueItemFields.PRODUCT_SKU,
            GoodsIssueItemFields.BATCH,
            GoodsIssueItemFields.BATCH_NO,
            GoodsIssueItemFields.QUANTITY,
            GoodsIssueItemFields.UNIT_PRICE,
            GoodsIssueItemFields.NOTE,
            GoodsIssueItemFields.CREATED_BY,
            GoodsIssueItemFields.UPDATED_BY,
            GoodsIssueItemFields.CREATED_AT,
            GoodsIssueItemFields.UPDATED_AT,
        ]
        read_only_fields = [
            GoodsIssueItemFields.ID,
            GoodsIssueItemFields.ISSUE_NO,
            GoodsIssueItemFields.PRODUCT_SKU,
            GoodsIssueItemFields.BATCH_NO,
            GoodsIssueItemFields.CREATED_AT,
            GoodsIssueItemFields.UPDATED_AT,
        ]


class StockMovementSerializer(serializers.ModelSerializer):
    warehouse_code = serializers.CharField(source="warehouse.code", read_only=True)
    product_sku = serializers.CharField(source="product.sku", read_only=True)
    product_name = serializers.CharField(source="product.name", read_only=True)
    batch_no = serializers.CharField(source="batch.batch_no", read_only=True)
    serial_number_value = serializers.CharField(source="serial_number.serial_number", read_only=True)

    class Meta:
        model = StockMovement
        fields = [
            StockMovementFields.ID,
            StockMovementFields.WAREHOUSE,
            StockMovementFields.WAREHOUSE_CODE,
            StockMovementFields.PRODUCT,
            StockMovementFields.PRODUCT_SKU,
            StockMovementFields.PRODUCT_NAME,
            StockMovementFields.BATCH,
            StockMovementFields.BATCH_NO,
            StockMovementFields.SERIAL_NUMBER,
            "serial_number_value",
            StockMovementFields.GOODS_RECEIPT,
            StockMovementFields.GOODS_ISSUE,
            StockMovementFields.STOCK_TRANSFER,
            StockMovementFields.STOCK_COUNT,
            StockMovementFields.MOVEMENT_TYPE,
            StockMovementFields.QUANTITY,
            StockMovementFields.MOVEMENT_AT,
            StockMovementFields.REFERENCE_NO,
            StockMovementFields.REASON_CODE,
            StockMovementFields.QUANTITY_BEFORE,
            StockMovementFields.QUANTITY_AFTER,
            StockMovementFields.NOTE,
            StockMovementFields.CREATED_BY,
            StockMovementFields.UPDATED_BY,
            StockMovementFields.CREATED_AT,
            StockMovementFields.UPDATED_AT,
        ]
        read_only_fields = [
            StockMovementFields.ID,
            StockMovementFields.WAREHOUSE_CODE,
            StockMovementFields.PRODUCT_SKU,
            StockMovementFields.PRODUCT_NAME,
            StockMovementFields.BATCH_NO,
            "serial_number_value",
            StockMovementFields.MOVEMENT_AT,
            StockMovementFields.QUANTITY_BEFORE,
            StockMovementFields.QUANTITY_AFTER,
            StockMovementFields.CREATED_AT,
            StockMovementFields.UPDATED_AT,
        ]

    def validate(self, attrs):
        movement_type = attrs.get("movement_type")
        warehouse = attrs.get("warehouse")
        product = attrs.get("product")
        quantity = attrs.get("quantity")

        if movement_type == StockMovement.MOVEMENT_OUT:
            inventory = Inventory.objects.filter(warehouse=warehouse, product=product).first()
            current_quantity = inventory.available_quantity if inventory else 0
            if quantity > current_quantity:
                raise serializers.ValidationError(
                    {"quantity": "Số lượng xuất vượt quá tồn khả dụng hiện tại."}
                )

        return attrs


class StockTransferSerializer(serializers.ModelSerializer):
    source_warehouse_code = serializers.CharField(source="source_warehouse.code", read_only=True)
    destination_warehouse_code = serializers.CharField(
        source="destination_warehouse.code",
        read_only=True,
    )

    class Meta:
        model = StockTransfer
        fields = [
            StockTransferFields.ID,
            StockTransferFields.TRANSFER_NO,
            StockTransferFields.SOURCE_WAREHOUSE,
            StockTransferFields.SOURCE_WAREHOUSE_CODE,
            StockTransferFields.DESTINATION_WAREHOUSE,
            StockTransferFields.DESTINATION_WAREHOUSE_CODE,
            StockTransferFields.STATUS,
            StockTransferFields.TRANSFERRED_AT,
            StockTransferFields.RECEIVED_AT,
            StockTransferFields.NOTE,
            StockTransferFields.APPROVED_BY,
            StockTransferFields.RECEIVED_BY,
            StockTransferFields.CREATED_BY,
            StockTransferFields.UPDATED_BY,
            StockTransferFields.CREATED_AT,
            StockTransferFields.UPDATED_AT,
        ]
        read_only_fields = [
            StockTransferFields.ID,
            StockTransferFields.SOURCE_WAREHOUSE_CODE,
            StockTransferFields.DESTINATION_WAREHOUSE_CODE,
            StockTransferFields.CREATED_AT,
            StockTransferFields.UPDATED_AT,
        ]

    def validate(self, attrs):
        source_warehouse = attrs.get("source_warehouse")
        destination_warehouse = attrs.get("destination_warehouse")
        if source_warehouse and destination_warehouse and source_warehouse == destination_warehouse:
            raise serializers.ValidationError(
                {"destination_warehouse": "Kho nhận phải khác kho xuất."}
            )
        return attrs


class StockTransferItemSerializer(serializers.ModelSerializer):
    transfer_no = serializers.CharField(source="transfer.transfer_no", read_only=True)
    product_sku = serializers.CharField(source="product.sku", read_only=True)
    batch_no = serializers.CharField(source="batch.batch_no", read_only=True)

    class Meta:
        model = StockTransferItem
        fields = [
            StockTransferItemFields.ID,
            StockTransferItemFields.TRANSFER,
            StockTransferItemFields.TRANSFER_NO,
            StockTransferItemFields.PRODUCT,
            StockTransferItemFields.PRODUCT_SKU,
            StockTransferItemFields.BATCH,
            StockTransferItemFields.BATCH_NO,
            StockTransferItemFields.QUANTITY,
            StockTransferItemFields.CREATED_BY,
            StockTransferItemFields.UPDATED_BY,
            StockTransferItemFields.CREATED_AT,
            StockTransferItemFields.UPDATED_AT,
        ]
        read_only_fields = [
            StockTransferItemFields.ID,
            StockTransferItemFields.TRANSFER_NO,
            StockTransferItemFields.PRODUCT_SKU,
            StockTransferItemFields.BATCH_NO,
            StockTransferItemFields.CREATED_AT,
            StockTransferItemFields.UPDATED_AT,
        ]


class StockCountSerializer(serializers.ModelSerializer):
    warehouse_code = serializers.CharField(source="warehouse.code", read_only=True)

    class Meta:
        model = StockCount
        fields = [
            StockCountFields.ID,
            StockCountFields.COUNT_NO,
            StockCountFields.WAREHOUSE,
            StockCountFields.WAREHOUSE_CODE,
            StockCountFields.COUNTED_AT,
            StockCountFields.STATUS,
            StockCountFields.NOTE,
            StockCountFields.COUNTED_BY,
            StockCountFields.APPROVED_BY,
            StockCountFields.CREATED_BY,
            StockCountFields.UPDATED_BY,
            StockCountFields.CREATED_AT,
            StockCountFields.UPDATED_AT,
        ]
        read_only_fields = [
            StockCountFields.ID,
            StockCountFields.WAREHOUSE_CODE,
            StockCountFields.CREATED_AT,
            StockCountFields.UPDATED_AT,
        ]


class StockCountItemSerializer(serializers.ModelSerializer):
    count_no = serializers.CharField(source="stock_count.count_no", read_only=True)
    product_sku = serializers.CharField(source="product.sku", read_only=True)
    batch_no = serializers.CharField(source="batch.batch_no", read_only=True)

    class Meta:
        model = StockCountItem
        fields = [
            StockCountItemFields.ID,
            StockCountItemFields.STOCK_COUNT,
            StockCountItemFields.COUNT_NO,
            StockCountItemFields.PRODUCT,
            StockCountItemFields.PRODUCT_SKU,
            StockCountItemFields.BATCH,
            StockCountItemFields.BATCH_NO,
            StockCountItemFields.EXPECTED_QUANTITY,
            StockCountItemFields.COUNTED_QUANTITY,
            StockCountItemFields.DIFFERENCE_QUANTITY,
            StockCountItemFields.NOTE,
            StockCountItemFields.CREATED_BY,
            StockCountItemFields.UPDATED_BY,
            StockCountItemFields.CREATED_AT,
            StockCountItemFields.UPDATED_AT,
        ]
        read_only_fields = [
            StockCountItemFields.ID,
            StockCountItemFields.COUNT_NO,
            StockCountItemFields.PRODUCT_SKU,
            StockCountItemFields.BATCH_NO,
            StockCountItemFields.CREATED_AT,
            StockCountItemFields.UPDATED_AT,
        ]

    def validate(self, attrs):
        expected_quantity = attrs.get("expected_quantity")
        counted_quantity = attrs.get("counted_quantity")

        if expected_quantity is not None and counted_quantity is not None:
            attrs["difference_quantity"] = counted_quantity - expected_quantity

        return attrs


class StockOperationSerializer(serializers.Serializer):
    warehouse = serializers.PrimaryKeyRelatedField(queryset=Warehouse.objects.all())
    product = serializers.PrimaryKeyRelatedField(queryset=Product.objects.all())
    batch = serializers.PrimaryKeyRelatedField(
        queryset=ProductBatch.objects.all(),
        required=False,
        allow_null=True,
    )
    serial_number = serializers.PrimaryKeyRelatedField(
        queryset=SerialNumber.objects.all(),
        required=False,
        allow_null=True,
    )
    quantity = serializers.IntegerField(min_value=0)
    reference_no = serializers.CharField(max_length=50, allow_blank=True, required=False)
    reason_code = serializers.ChoiceField(
        choices=StockMovement.REASON_CHOICES,
        required=False,
        default=StockMovement.REASON_MANUAL,
    )
    note = serializers.CharField(max_length=255, allow_blank=True, required=False)

    def validate(self, attrs):
        movement_type = self.context.get("movement_type")
        warehouse = attrs["warehouse"]
        product = attrs["product"]
        quantity = attrs["quantity"]
        batch = attrs.get("batch")
        serial_number = attrs.get("serial_number")

        if movement_type in {StockMovement.MOVEMENT_IN, StockMovement.MOVEMENT_OUT} and quantity < 1:
            raise serializers.ValidationError({"quantity": "Số lượng phải lớn hơn 0."})

        if batch and batch.product_id != product.id:
            raise serializers.ValidationError({"batch": "Batch không thuộc sản phẩm đã chọn."})

        if batch and batch.warehouse_id != warehouse.id:
            raise serializers.ValidationError({"batch": "Batch không thuộc kho đã chọn."})

        if serial_number and serial_number.product_id != product.id:
            raise serializers.ValidationError(
                {"serial_number": "Serial number không thuộc sản phẩm đã chọn."}
            )

        if serial_number and serial_number.warehouse_id != warehouse.id:
            raise serializers.ValidationError(
                {"serial_number": "Serial number không thuộc kho đã chọn."}
            )

        if movement_type == StockMovement.MOVEMENT_OUT:
            inventory = Inventory.objects.filter(warehouse=warehouse, product=product).first()
            current_quantity = inventory.available_quantity if inventory else 0
            if quantity > current_quantity:
                raise serializers.ValidationError(
                    {"quantity": "Số lượng xuất vượt quá tồn khả dụng hiện tại."}
                )

        return attrs


class QRLookupSerializer(serializers.Serializer):
    code = serializers.CharField(max_length=2048)


class QRCodeResponseSerializer(serializers.Serializer):
    label = serializers.CharField()
    payload = serializers.JSONField()
    image_base64 = serializers.CharField()


class ForecastDemandQuerySerializer(serializers.Serializer):
    product_id = serializers.IntegerField(min_value=1)
    warehouse_id = serializers.IntegerField(min_value=1, required=False)
    days = serializers.IntegerField(min_value=1, max_value=180, default=30)


class SlottingItemRequestSerializer(serializers.Serializer):
    product_id = serializers.IntegerField(min_value=1)
    quantity = serializers.IntegerField(min_value=1)


class SlottingOptimizationSerializer(serializers.Serializer):
    shelf_ids = serializers.ListField(
        child=serializers.IntegerField(min_value=1),
        allow_empty=False,
    )
    items = SlottingItemRequestSerializer(many=True, allow_empty=False)


class OperationsDashboardQuerySerializer(serializers.Serializer):
    warehouse_id = serializers.IntegerField(min_value=1, required=False)
