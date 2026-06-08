from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import (
    CategoryViewSet,
    GoodsIssueItemViewSet,
    GoodsIssueViewSet,
    GoodsReceiptItemViewSet,
    GoodsReceiptViewSet,
    InventoryViewSet,
    ProductBatchViewSet,
    ProductViewSet,
    SerialNumberViewSet,
    StockCountItemViewSet,
    StockCountViewSet,
    StockMovementViewSet,
    StockTransferItemViewSet,
    StockTransferViewSet,
    SupplierViewSet,
    WarehouseViewSet,
    dashboard_summary,
    forecast_demand,
    operations_dashboard,
    optimize_slotting,
    qr_lookup,
)

router = DefaultRouter()
router.register("categories", CategoryViewSet, basename="category")
router.register("suppliers", SupplierViewSet, basename="supplier")
router.register("warehouses", WarehouseViewSet, basename="warehouse")
router.register("products", ProductViewSet, basename="product")
router.register("inventories", InventoryViewSet, basename="inventory")
router.register("product-batches", ProductBatchViewSet, basename="product-batch")
router.register("serial-numbers", SerialNumberViewSet, basename="serial-number")
router.register("goods-receipts", GoodsReceiptViewSet, basename="goods-receipt")
router.register("goods-receipt-items", GoodsReceiptItemViewSet, basename="goods-receipt-item")
router.register("goods-issues", GoodsIssueViewSet, basename="goods-issue")
router.register("goods-issue-items", GoodsIssueItemViewSet, basename="goods-issue-item")
router.register("stock-movements", StockMovementViewSet, basename="stock-movement")
router.register("stock-transfers", StockTransferViewSet, basename="stock-transfer")
router.register("stock-transfer-items", StockTransferItemViewSet, basename="stock-transfer-item")
router.register("stock-counts", StockCountViewSet, basename="stock-count")
router.register("stock-count-items", StockCountItemViewSet, basename="stock-count-item")

urlpatterns = [
    path("dashboard/", dashboard_summary, name="dashboard-summary"),
    path("ai/forecast-demand/", forecast_demand, name="forecast-demand"),
    path("ai/slotting/optimize/", optimize_slotting, name="optimize-slotting"),
    path("ai/operations/dashboard/", operations_dashboard, name="operations-dashboard"),
    path("qr/lookup/", qr_lookup, name="qr-lookup"),
    path("", include(router.urls)),
]
