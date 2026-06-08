import base64
import io
import json

import qrcode
from django.db import transaction
from django.db.models import F, Sum
from django.utils import timezone
from rest_framework import status, viewsets
from rest_framework.decorators import action, api_view
from rest_framework.response import Response

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
from .serializers import (
    CategorySerializer,
    ForecastDemandQuerySerializer,
    GoodsIssueItemSerializer,
    GoodsIssueSerializer,
    GoodsReceiptItemSerializer,
    GoodsReceiptSerializer,
    InventorySerializer,
    OperationsDashboardQuerySerializer,
    ProductBatchSerializer,
    ProductSerializer,
    QRLookupSerializer,
    SerialNumberSerializer,
    SlottingOptimizationSerializer,
    StockCountItemSerializer,
    StockCountSerializer,
    StockMovementSerializer,
    StockOperationSerializer,
    StockTransferItemSerializer,
    StockTransferSerializer,
    SupplierSerializer,
    WarehouseSerializer,
)
from .services.forecasting import forecast_product_demand
from .services.operations import build_operations_dashboard
from .services.slotting import optimize_shelf_space


def build_qr_image_base64(payload):
    qr = qrcode.QRCode(version=1, box_size=10, border=4)
    qr.add_data(json.dumps(payload, ensure_ascii=False))
    qr.make(fit=True)

    image = qr.make_image(fill_color="black", back_color="white")
    buffer = io.BytesIO()
    image.save(buffer, format="PNG")
    return base64.b64encode(buffer.getvalue()).decode("utf-8")


def serialize_qr_response(label, payload):
    return {
        "label": label,
        "payload": payload,
        "image_base64": build_qr_image_base64(payload),
    }


def update_batch_inventory(*, batch, movement_type, quantity):
    if not batch:
        return

    if movement_type == StockMovement.MOVEMENT_IN:
        batch.quantity += quantity
    elif movement_type == StockMovement.MOVEMENT_OUT:
        batch.quantity = max(batch.quantity - quantity, 0)
    elif movement_type == StockMovement.MOVEMENT_ADJUST:
        batch.quantity = quantity

    batch.save(update_fields=["quantity", "updated_at"])


def update_serial_status(*, serial_number, movement_type):
    if not serial_number:
        return

    if movement_type == StockMovement.MOVEMENT_IN:
        serial_number.status = SerialNumber.STATUS_IN_STOCK
    elif movement_type == StockMovement.MOVEMENT_OUT:
        serial_number.status = SerialNumber.STATUS_SOLD
    elif movement_type == StockMovement.MOVEMENT_ADJUST:
        serial_number.status = SerialNumber.STATUS_IN_STOCK

    serial_number.save(update_fields=["status", "updated_at"])


def apply_stock_movement(
    *,
    warehouse,
    product,
    movement_type,
    quantity,
    note="",
    batch=None,
    serial_number=None,
    reference_no="",
    reason_code=StockMovement.REASON_MANUAL,
    goods_receipt=None,
    goods_issue=None,
    stock_transfer=None,
    stock_count=None,
):
    inventory, _ = Inventory.objects.get_or_create(
        warehouse=warehouse,
        product=product,
        defaults={
            "quantity": 0,
            "reserved_quantity": 0,
            "damaged_quantity": 0,
            "reorder_level": 0,
            "safety_stock": 0,
            "max_stock_level": 0,
            "bin_location": "",
        },
    )

    quantity_before = inventory.quantity

    if movement_type == StockMovement.MOVEMENT_IN:
        inventory.quantity += quantity
    elif movement_type == StockMovement.MOVEMENT_OUT:
        inventory.quantity -= quantity
    elif movement_type == StockMovement.MOVEMENT_ADJUST:
        inventory.quantity = quantity
        inventory.last_counted_at = timezone.now()

    inventory.save()

    update_batch_inventory(batch=batch, movement_type=movement_type, quantity=quantity)
    update_serial_status(serial_number=serial_number, movement_type=movement_type)

    movement = StockMovement.objects.create(
        warehouse=warehouse,
        product=product,
        batch=batch,
        serial_number=serial_number,
        goods_receipt=goods_receipt,
        goods_issue=goods_issue,
        stock_transfer=stock_transfer,
        stock_count=stock_count,
        movement_type=movement_type,
        quantity=quantity,
        reference_no=reference_no,
        reason_code=reason_code,
        quantity_before=quantity_before,
        quantity_after=inventory.quantity,
        note=note,
    )

    return movement, inventory


class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.select_related("parent").all()
    serializer_class = CategorySerializer


class SupplierViewSet(viewsets.ModelViewSet):
    queryset = Supplier.objects.all()
    serializer_class = SupplierSerializer


class WarehouseViewSet(viewsets.ModelViewSet):
    queryset = Warehouse.objects.all()
    serializer_class = WarehouseSerializer


class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.select_related("category", "supplier").all()
    serializer_class = ProductSerializer

    @action(detail=True, methods=["GET"], url_path="qr")
    def qr(self, request, pk=None):
        product = self.get_object()
        serializer = self.get_serializer(product)

        return Response(
            serialize_qr_response(
                label=serializer.data["qr_label"],
                payload=serializer.data["qr_payload"],
            )
        )


class InventoryViewSet(viewsets.ModelViewSet):
    queryset = Inventory.objects.select_related("warehouse", "product").all()
    serializer_class = InventorySerializer

    def get_queryset(self):
        queryset = super().get_queryset()
        warehouse_id = self.request.query_params.get("warehouse")
        product_id = self.request.query_params.get("product")
        below_reorder = self.request.query_params.get("below_reorder")

        if warehouse_id:
            queryset = queryset.filter(warehouse_id=warehouse_id)
        if product_id:
            queryset = queryset.filter(product_id=product_id)
        if below_reorder in {"1", "true", "True"}:
            queryset = queryset.filter(quantity__lte=F("reorder_level"))

        return queryset

    @action(detail=False, methods=["GET"], url_path="low-stock")
    def low_stock(self, request):
        queryset = self.get_queryset().filter(quantity__lte=F("reorder_level"))
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=["GET"], url_path="qr")
    def qr(self, request, pk=None):
        inventory = self.get_object()
        serializer = self.get_serializer(inventory)

        return Response(
            serialize_qr_response(
                label=serializer.data["qr_label"],
                payload=serializer.data["qr_payload"],
            )
        )


class ProductBatchViewSet(viewsets.ModelViewSet):
    queryset = ProductBatch.objects.select_related("product", "warehouse", "supplier").all()
    serializer_class = ProductBatchSerializer

    def get_queryset(self):
        queryset = super().get_queryset()
        warehouse_id = self.request.query_params.get("warehouse")
        product_id = self.request.query_params.get("product")
        expiring = self.request.query_params.get("expiring")

        if warehouse_id:
            queryset = queryset.filter(warehouse_id=warehouse_id)
        if product_id:
            queryset = queryset.filter(product_id=product_id)
        if expiring in {"1", "true", "True"}:
            queryset = queryset.filter(expiry_date__isnull=False).order_by("expiry_date")

        return queryset


class SerialNumberViewSet(viewsets.ModelViewSet):
    queryset = SerialNumber.objects.select_related("product", "warehouse", "batch").all()
    serializer_class = SerialNumberSerializer

    def get_queryset(self):
        queryset = super().get_queryset()
        warehouse_id = self.request.query_params.get("warehouse")
        product_id = self.request.query_params.get("product")
        status_value = self.request.query_params.get("status")

        if warehouse_id:
            queryset = queryset.filter(warehouse_id=warehouse_id)
        if product_id:
            queryset = queryset.filter(product_id=product_id)
        if status_value:
            queryset = queryset.filter(status=status_value)

        return queryset


class StockMovementViewSet(viewsets.ModelViewSet):
    queryset = StockMovement.objects.select_related(
        "warehouse",
        "product",
        "batch",
        "serial_number",
    ).all()
    serializer_class = StockMovementSerializer

    def get_queryset(self):
        queryset = super().get_queryset()
        warehouse_id = self.request.query_params.get("warehouse")
        product_id = self.request.query_params.get("product")
        movement_type = self.request.query_params.get("movement_type")
        reason_code = self.request.query_params.get("reason_code")

        if warehouse_id:
            queryset = queryset.filter(warehouse_id=warehouse_id)
        if product_id:
            queryset = queryset.filter(product_id=product_id)
        if movement_type:
            queryset = queryset.filter(movement_type=movement_type)
        if reason_code:
            queryset = queryset.filter(reason_code=reason_code)

        return queryset

    @transaction.atomic
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        movement, _inventory = apply_stock_movement(
            warehouse=serializer.validated_data["warehouse"],
            product=serializer.validated_data["product"],
            movement_type=serializer.validated_data["movement_type"],
            quantity=serializer.validated_data["quantity"],
            batch=serializer.validated_data.get("batch"),
            serial_number=serializer.validated_data.get("serial_number"),
            reference_no=serializer.validated_data.get("reference_no", ""),
            reason_code=serializer.validated_data.get(
                "reason_code", StockMovement.REASON_MANUAL
            ),
            note=serializer.validated_data.get("note", ""),
        )

        output_serializer = self.get_serializer(movement)
        headers = self.get_success_headers(output_serializer.data)
        return Response(output_serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    @transaction.atomic
    @action(detail=False, methods=["POST"], url_path="stock-in")
    def stock_in(self, request):
        serializer = StockOperationSerializer(
            data=request.data,
            context={"movement_type": StockMovement.MOVEMENT_IN},
        )
        serializer.is_valid(raise_exception=True)

        movement, inventory = apply_stock_movement(
            warehouse=serializer.validated_data["warehouse"],
            product=serializer.validated_data["product"],
            movement_type=StockMovement.MOVEMENT_IN,
            quantity=serializer.validated_data["quantity"],
            batch=serializer.validated_data.get("batch"),
            serial_number=serializer.validated_data.get("serial_number"),
            reference_no=serializer.validated_data.get("reference_no", ""),
            reason_code=serializer.validated_data.get(
                "reason_code", StockMovement.REASON_MANUAL
            ),
            note=serializer.validated_data.get("note", ""),
        )

        return Response(
            {
                "movement": self.get_serializer(movement).data,
                "inventory": InventorySerializer(inventory).data,
            },
            status=status.HTTP_201_CREATED,
        )

    @transaction.atomic
    @action(detail=False, methods=["POST"], url_path="stock-out")
    def stock_out(self, request):
        serializer = StockOperationSerializer(
            data=request.data,
            context={"movement_type": StockMovement.MOVEMENT_OUT},
        )
        serializer.is_valid(raise_exception=True)

        movement, inventory = apply_stock_movement(
            warehouse=serializer.validated_data["warehouse"],
            product=serializer.validated_data["product"],
            movement_type=StockMovement.MOVEMENT_OUT,
            quantity=serializer.validated_data["quantity"],
            batch=serializer.validated_data.get("batch"),
            serial_number=serializer.validated_data.get("serial_number"),
            reference_no=serializer.validated_data.get("reference_no", ""),
            reason_code=serializer.validated_data.get(
                "reason_code", StockMovement.REASON_MANUAL
            ),
            note=serializer.validated_data.get("note", ""),
        )

        return Response(
            {
                "movement": self.get_serializer(movement).data,
                "inventory": InventorySerializer(inventory).data,
            },
            status=status.HTTP_201_CREATED,
        )

    @transaction.atomic
    @action(detail=False, methods=["POST"], url_path="adjust")
    def adjust(self, request):
        serializer = StockOperationSerializer(
            data=request.data,
            context={"movement_type": StockMovement.MOVEMENT_ADJUST},
        )
        serializer.is_valid(raise_exception=True)

        movement, inventory = apply_stock_movement(
            warehouse=serializer.validated_data["warehouse"],
            product=serializer.validated_data["product"],
            movement_type=StockMovement.MOVEMENT_ADJUST,
            quantity=serializer.validated_data["quantity"],
            batch=serializer.validated_data.get("batch"),
            serial_number=serializer.validated_data.get("serial_number"),
            reference_no=serializer.validated_data.get("reference_no", ""),
            reason_code=serializer.validated_data.get(
                "reason_code", StockMovement.REASON_STOCK_COUNT
            ),
            note=serializer.validated_data.get("note", ""),
        )

        return Response(
            {
                "movement": self.get_serializer(movement).data,
                "inventory": InventorySerializer(inventory).data,
            },
            status=status.HTTP_201_CREATED,
        )


class GoodsReceiptViewSet(viewsets.ModelViewSet):
    queryset = GoodsReceipt.objects.select_related("warehouse", "supplier").all()
    serializer_class = GoodsReceiptSerializer


class GoodsReceiptItemViewSet(viewsets.ModelViewSet):
    queryset = GoodsReceiptItem.objects.select_related(
        "goods_receipt",
        "product",
        "batch",
    ).all()
    serializer_class = GoodsReceiptItemSerializer


class GoodsIssueViewSet(viewsets.ModelViewSet):
    queryset = GoodsIssue.objects.select_related("warehouse").all()
    serializer_class = GoodsIssueSerializer


class GoodsIssueItemViewSet(viewsets.ModelViewSet):
    queryset = GoodsIssueItem.objects.select_related(
        "goods_issue",
        "product",
        "batch",
    ).all()
    serializer_class = GoodsIssueItemSerializer


class StockTransferViewSet(viewsets.ModelViewSet):
    queryset = StockTransfer.objects.select_related(
        "source_warehouse",
        "destination_warehouse",
    ).all()
    serializer_class = StockTransferSerializer


class StockTransferItemViewSet(viewsets.ModelViewSet):
    queryset = StockTransferItem.objects.select_related(
        "transfer",
        "product",
        "batch",
    ).all()
    serializer_class = StockTransferItemSerializer


class StockCountViewSet(viewsets.ModelViewSet):
    queryset = StockCount.objects.select_related("warehouse").all()
    serializer_class = StockCountSerializer


class StockCountItemViewSet(viewsets.ModelViewSet):
    queryset = StockCountItem.objects.select_related(
        "stock_count",
        "product",
        "batch",
    ).all()
    serializer_class = StockCountItemSerializer


@api_view(["GET"])
def dashboard_summary(request):
    total_warehouses = Warehouse.objects.count()
    total_products = Product.objects.count()
    total_inventory_units = Inventory.objects.aggregate(total=Sum("quantity"))["total"] or 0
    low_stock_items = Inventory.objects.filter(quantity__lte=F("reorder_level")).count()
    total_suppliers = Supplier.objects.count()
    total_batches = ProductBatch.objects.count()
    total_serial_numbers = SerialNumber.objects.count()

    recent_movements = StockMovement.objects.select_related(
        "warehouse",
        "product",
        "batch",
        "serial_number",
    )[:10]

    return Response(
        {
            "total_warehouses": total_warehouses,
            "total_products": total_products,
            "total_suppliers": total_suppliers,
            "total_batches": total_batches,
            "total_serial_numbers": total_serial_numbers,
            "total_inventory_units": total_inventory_units,
            "low_stock_items": low_stock_items,
            "recent_movements": [
                {
                    "id": movement.id,
                    "warehouse": movement.warehouse.code,
                    "product": movement.product.sku,
                    "batch_no": movement.batch.batch_no if movement.batch else None,
                    "serial_number": (
                        movement.serial_number.serial_number if movement.serial_number else None
                    ),
                    "movement_type": movement.movement_type,
                    "quantity": movement.quantity,
                    "quantity_before": movement.quantity_before,
                    "quantity_after": movement.quantity_after,
                    "reference_no": movement.reference_no,
                    "reason_code": movement.reason_code,
                    "note": movement.note,
                    "movement_at": movement.movement_at,
                }
                for movement in recent_movements
            ],
        }
    )


@api_view(["GET"])
def forecast_demand(request):
    serializer = ForecastDemandQuerySerializer(data=request.query_params)
    serializer.is_valid(raise_exception=True)

    data = forecast_product_demand(
        product_id=serializer.validated_data["product_id"],
        periods=serializer.validated_data["days"],
        warehouse_id=serializer.validated_data.get("warehouse_id"),
    )
    return Response(data)


@api_view(["POST"])
def optimize_slotting(request):
    serializer = SlottingOptimizationSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)

    result = optimize_shelf_space(
        shelf_ids=serializer.validated_data["shelf_ids"],
        item_requests=serializer.validated_data["items"],
    )
    response_status = status.HTTP_200_OK
    if result.get("status") == "error":
        response_status = status.HTTP_400_BAD_REQUEST

    return Response(result, status=response_status)


@api_view(["GET"])
def operations_dashboard(request):
    serializer = OperationsDashboardQuerySerializer(data=request.query_params)
    serializer.is_valid(raise_exception=True)

    data = build_operations_dashboard(
        warehouse_id=serializer.validated_data.get("warehouse_id"),
    )
    return Response(data)


@api_view(["POST"])
def qr_lookup(request):
    serializer = QRLookupSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)

    code = serializer.validated_data["code"].strip()

    try:
        payload = json.loads(code)
    except json.JSONDecodeError:
        payload = None

    if isinstance(payload, dict):
        qr_type = payload.get("type")

        if qr_type == "product":
            product = None
            product_id = payload.get("product_id")
            sku = payload.get("sku")

            if product_id is not None:
                product = Product.objects.filter(id=product_id).first()
            if not product and sku:
                product = Product.objects.filter(sku=sku).first()
            if not product:
                return Response({"detail": "Không tìm thấy sản phẩm từ QR code."}, status=404)

            return Response(
                {
                    "type": "product",
                    "data": ProductSerializer(product).data,
                }
            )

        if qr_type == "inventory":
            inventory = None
            inventory_id = payload.get("inventory_id")
            warehouse_id = payload.get("warehouse_id")
            product_id = payload.get("product_id")
            warehouse_code = payload.get("warehouse_code")
            sku = payload.get("sku")

            if inventory_id is not None:
                inventory = (
                    Inventory.objects.select_related("warehouse", "product")
                    .filter(id=inventory_id)
                    .first()
                )
            if not inventory and warehouse_id is not None and product_id is not None:
                inventory = (
                    Inventory.objects.select_related("warehouse", "product")
                    .filter(warehouse_id=warehouse_id, product_id=product_id)
                    .first()
                )
            if not inventory and warehouse_code and sku:
                inventory = (
                    Inventory.objects.select_related("warehouse", "product")
                    .filter(warehouse__code=warehouse_code, product__sku=sku)
                    .first()
                )
            if not inventory:
                return Response({"detail": "Không tìm thấy tồn kho từ QR code."}, status=404)

            return Response(
                {
                    "type": "inventory",
                    "data": InventorySerializer(inventory).data,
                }
            )

        return Response({"detail": "QR JSON không được hỗ trợ."}, status=400)

    if code.startswith("PRODUCT:"):
        sku = code.split(":", 1)[1]
        product = Product.objects.filter(sku=sku).first()
        if not product:
            return Response({"detail": "Không tìm thấy sản phẩm từ QR code."}, status=404)

        return Response(
            {
                "type": "product",
                "data": ProductSerializer(product).data,
            }
        )

    if code.startswith("INV:"):
        parts = code.split(":")
        if len(parts) != 3:
            return Response({"detail": "QR inventory không hợp lệ."}, status=400)

        _, warehouse_code, sku = parts
        inventory = (
            Inventory.objects.select_related("warehouse", "product")
            .filter(warehouse__code=warehouse_code, product__sku=sku)
            .first()
        )
        if not inventory:
            return Response({"detail": "Không tìm thấy tồn kho từ QR code."}, status=404)

        return Response(
            {
                "type": "inventory",
                "data": InventorySerializer(inventory).data,
            }
        )

    return Response(
        {
            "detail": "QR code không được hỗ trợ. Dùng PRODUCT:<SKU>, INV:<WAREHOUSE_CODE>:<SKU> hoặc JSON payload."
        },
        status=400,
    )