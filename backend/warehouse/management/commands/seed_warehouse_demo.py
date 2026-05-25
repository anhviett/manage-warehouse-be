from decimal import Decimal

from django.core.management.base import BaseCommand
from django.db import transaction

from warehouse.models import (
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


class Command(BaseCommand):
    help = "Seed practical demo data for warehouse management trial usage."

    @transaction.atomic
    def handle(self, *args, **options):
        self.stdout.write("Seeding warehouse demo data...")

        category_map = self.seed_categories()
        supplier_map = self.seed_suppliers()
        warehouse_map = self.seed_warehouses()
        product_map = self.seed_products(category_map, supplier_map)

        inventory_map = self.seed_inventory_snapshots(warehouse_map, product_map)
        batch_map = self.seed_batches(warehouse_map, product_map, supplier_map)
        self.seed_serial_numbers(warehouse_map, product_map, batch_map)

        self.seed_goods_receipts(warehouse_map, supplier_map, product_map, batch_map)
        self.seed_goods_issues(warehouse_map, product_map, batch_map)
        self.seed_stock_transfers(warehouse_map, product_map, batch_map)
        self.seed_stock_counts(warehouse_map, product_map, batch_map)
        self.seed_stock_movements(warehouse_map, product_map, batch_map, inventory_map)

        self.print_summary()

    def seed_categories(self):
        categories_data = [
            {
                "name": "Devices",
                "slug": "devices",
                "description": "Warehouse operation devices and scanners.",
                "is_active": True,
                "parent": None,
            },
            {
                "name": "Consumables",
                "slug": "consumables",
                "description": "Consumable goods for packing and daily operation.",
                "is_active": True,
                "parent": None,
            },
            {
                "name": "Safety",
                "slug": "safety",
                "description": "Warehouse safety and protective equipment.",
                "is_active": True,
                "parent": None,
            },
        ]

        category_map = {}
        for data in categories_data:
            category, _created = Category.objects.update_or_create(
                slug=data["slug"],
                defaults=data,
            )
            category_map[category.slug] = category
        return category_map

    def seed_suppliers(self):
        suppliers_data = [
            {
                "code": "SUP-TECH",
                "name": "Tech Supply Co.",
                "contact_name": "Nguyen Minh Quan",
                "phone": "0901000001",
                "email": "tech-supply@example.com",
                "address": "Ha Noi",
                "is_active": True,
            },
            {
                "code": "SUP-PACK",
                "name": "Packing Materials JSC",
                "contact_name": "Tran Thi Lan",
                "phone": "0901000002",
                "email": "packing@example.com",
                "address": "Binh Duong",
                "is_active": True,
            },
            {
                "code": "SUP-SAFE",
                "name": "Safe Work Vietnam",
                "contact_name": "Le Hoang Nam",
                "phone": "0901000003",
                "email": "safe-work@example.com",
                "address": "Ho Chi Minh City",
                "is_active": True,
            },
        ]

        supplier_map = {}
        for data in suppliers_data:
            supplier, _created = Supplier.objects.update_or_create(
                code=data["code"],
                defaults=data,
            )
            supplier_map[supplier.code] = supplier
        return supplier_map

    def seed_warehouses(self):
        warehouses_data = [
            {
                "code": "WH-HN",
                "name": "Hanoi Warehouse",
                "address": "Cau Giay, Ha Noi",
                "manager_name": "Nguyen Van A",
                "is_active": True,
            },
            {
                "code": "WH-HCM",
                "name": "HCM Warehouse",
                "address": "Thu Duc, Ho Chi Minh",
                "manager_name": "Tran Thi B",
                "is_active": True,
            },
        ]

        warehouse_map = {}
        for data in warehouses_data:
            warehouse, _created = Warehouse.objects.update_or_create(
                code=data["code"],
                defaults=data,
            )
            warehouse_map[warehouse.code] = warehouse
        return warehouse_map

    def seed_products(self, category_map, supplier_map):
        products_data = [
            {
                "sku": "SP001",
                "name": "Barcode Scanner",
                "barcode": "893000000001",
                "category": category_map["devices"],
                "supplier": supplier_map["SUP-TECH"],
                "brand": "Zebra",
                "description": "2D handheld scanner for warehouse picking.",
                "unit": "pcs",
                "cost_price": Decimal("950000.00"),
                "selling_price": Decimal("1250000.00"),
                "track_batch": False,
                "track_serial": True,
                "shelf_life_days": 0,
                "is_active": True,
            },
            {
                "sku": "SP002",
                "name": "Thermal Label Printer",
                "barcode": "893000000002",
                "category": category_map["devices"],
                "supplier": supplier_map["SUP-TECH"],
                "brand": "TSC",
                "description": "Printer for QR and barcode labels.",
                "unit": "pcs",
                "cost_price": Decimal("2800000.00"),
                "selling_price": Decimal("3200000.00"),
                "track_batch": False,
                "track_serial": True,
                "shelf_life_days": 0,
                "is_active": True,
            },
            {
                "sku": "SP003",
                "name": "Packing Box M",
                "barcode": "893000000003",
                "category": category_map["consumables"],
                "supplier": supplier_map["SUP-PACK"],
                "brand": "PackPro",
                "description": "Medium-size carton box for shipment.",
                "unit": "box",
                "cost_price": Decimal("9000.00"),
                "selling_price": Decimal("12000.00"),
                "track_batch": True,
                "track_serial": False,
                "shelf_life_days": 365,
                "is_active": True,
            },
            {
                "sku": "SP004",
                "name": "Warehouse Gloves",
                "barcode": "893000000004",
                "category": category_map["safety"],
                "supplier": supplier_map["SUP-SAFE"],
                "brand": "SafeGrip",
                "description": "Safety gloves for warehouse workers.",
                "unit": "pair",
                "cost_price": Decimal("30000.00"),
                "selling_price": Decimal("45000.00"),
                "track_batch": True,
                "track_serial": False,
                "shelf_life_days": 730,
                "is_active": True,
            },
        ]

        product_map = {}
        for data in products_data:
            product, _created = Product.objects.update_or_create(
                sku=data["sku"],
                defaults=data,
            )
            product_map[product.sku] = product
        return product_map

    def seed_inventory_snapshots(self, warehouse_map, product_map):
        inventories_data = [
            {
                "warehouse_code": "WH-HN",
                "sku": "SP001",
                "quantity": 15,
                "reserved_quantity": 2,
                "damaged_quantity": 0,
                "reorder_level": 5,
                "safety_stock": 3,
                "max_stock_level": 40,
                "bin_location": "A1-SCN",
            },
            {
                "warehouse_code": "WH-HN",
                "sku": "SP002",
                "quantity": 6,
                "reserved_quantity": 1,
                "damaged_quantity": 0,
                "reorder_level": 2,
                "safety_stock": 1,
                "max_stock_level": 20,
                "bin_location": "A2-PRN",
            },
            {
                "warehouse_code": "WH-HN",
                "sku": "SP003",
                "quantity": 120,
                "reserved_quantity": 10,
                "damaged_quantity": 0,
                "reorder_level": 40,
                "safety_stock": 20,
                "max_stock_level": 300,
                "bin_location": "B1-BOX",
            },
            {
                "warehouse_code": "WH-HCM",
                "sku": "SP001",
                "quantity": 8,
                "reserved_quantity": 1,
                "damaged_quantity": 0,
                "reorder_level": 5,
                "safety_stock": 2,
                "max_stock_level": 30,
                "bin_location": "A1-SCN",
            },
            {
                "warehouse_code": "WH-HCM",
                "sku": "SP003",
                "quantity": 25,
                "reserved_quantity": 0,
                "damaged_quantity": 1,
                "reorder_level": 30,
                "safety_stock": 15,
                "max_stock_level": 120,
                "bin_location": "B2-BOX",
            },
            {
                "warehouse_code": "WH-HCM",
                "sku": "SP004",
                "quantity": 50,
                "reserved_quantity": 5,
                "damaged_quantity": 2,
                "reorder_level": 20,
                "safety_stock": 10,
                "max_stock_level": 150,
                "bin_location": "C1-SAFE",
            },
        ]

        inventory_map = {}
        for item in inventories_data:
            inventory, _created = Inventory.objects.update_or_create(
                warehouse=warehouse_map[item["warehouse_code"]],
                product=product_map[item["sku"]],
                defaults={
                    "quantity": item["quantity"],
                    "reserved_quantity": item["reserved_quantity"],
                    "damaged_quantity": item["damaged_quantity"],
                    "reorder_level": item["reorder_level"],
                    "safety_stock": item["safety_stock"],
                    "max_stock_level": item["max_stock_level"],
                    "bin_location": item["bin_location"],
                },
            )
            inventory_map[(item["warehouse_code"], item["sku"])] = inventory
        return inventory_map

    def seed_batches(self, warehouse_map, product_map, supplier_map):
        batches_data = [
            {
                "warehouse_code": "WH-HN",
                "sku": "SP003",
                "batch_no": "BOX-2026-01",
                "manufacturing_date": "2026-01-10",
                "expiry_date": "2027-01-10",
                "quantity": 80,
                "reserved_quantity": 10,
                "supplier_code": "SUP-PACK",
            },
            {
                "warehouse_code": "WH-HN",
                "sku": "SP003",
                "batch_no": "BOX-2026-02",
                "manufacturing_date": "2026-03-05",
                "expiry_date": "2027-03-05",
                "quantity": 40,
                "reserved_quantity": 0,
                "supplier_code": "SUP-PACK",
            },
            {
                "warehouse_code": "WH-HCM",
                "sku": "SP003",
                "batch_no": "BOX-2026-03",
                "manufacturing_date": "2026-02-12",
                "expiry_date": "2027-02-12",
                "quantity": 25,
                "reserved_quantity": 0,
                "supplier_code": "SUP-PACK",
            },
            {
                "warehouse_code": "WH-HCM",
                "sku": "SP004",
                "batch_no": "GLV-2026-01",
                "manufacturing_date": "2026-01-20",
                "expiry_date": "2028-01-20",
                "quantity": 50,
                "reserved_quantity": 5,
                "supplier_code": "SUP-SAFE",
            },
        ]

        batch_map = {}
        for item in batches_data:
            batch, _created = ProductBatch.objects.update_or_create(
                product=product_map[item["sku"]],
                warehouse=warehouse_map[item["warehouse_code"]],
                batch_no=item["batch_no"],
                defaults={
                    "manufacturing_date": item["manufacturing_date"],
                    "expiry_date": item["expiry_date"],
                    "quantity": item["quantity"],
                    "reserved_quantity": item["reserved_quantity"],
                    "supplier": supplier_map[item["supplier_code"]],
                },
            )
            batch_map[(item["warehouse_code"], item["sku"], item["batch_no"])] = batch
        return batch_map

    def seed_serial_numbers(self, warehouse_map, product_map, batch_map):
        serials_data = [
            {
                "serial_number": "SCN-HN-0001",
                "warehouse_code": "WH-HN",
                "sku": "SP001",
                "status": SerialNumber.STATUS_IN_STOCK,
            },
            {
                "serial_number": "SCN-HN-0002",
                "warehouse_code": "WH-HN",
                "sku": "SP001",
                "status": SerialNumber.STATUS_RESERVED,
            },
            {
                "serial_number": "SCN-HCM-0001",
                "warehouse_code": "WH-HCM",
                "sku": "SP001",
                "status": SerialNumber.STATUS_IN_STOCK,
            },
            {
                "serial_number": "PRN-HN-0001",
                "warehouse_code": "WH-HN",
                "sku": "SP002",
                "status": SerialNumber.STATUS_IN_STOCK,
            },
        ]

        for item in serials_data:
            SerialNumber.objects.update_or_create(
                serial_number=item["serial_number"],
                defaults={
                    "warehouse": warehouse_map[item["warehouse_code"]],
                    "product": product_map[item["sku"]],
                    "batch": None,
                    "status": item["status"],
                    "note": "Seed demo serial",
                },
            )

    def seed_goods_receipts(self, warehouse_map, supplier_map, product_map, batch_map):
        receipt, _created = GoodsReceipt.objects.update_or_create(
            receipt_no="GR-0001",
            defaults={
                "warehouse": warehouse_map["WH-HN"],
                "supplier": supplier_map["SUP-PACK"],
                "reference_no": "PO-DEMO-001",
                "status": GoodsReceipt.STATUS_POSTED,
                "note": "Initial receipt for consumables demo",
            },
        )

        GoodsReceiptItem.objects.update_or_create(
            goods_receipt=receipt,
            product=product_map["SP003"],
            batch=batch_map[("WH-HN", "SP003", "BOX-2026-01")],
            defaults={
                "quantity": 80,
                "unit_cost": Decimal("9000.00"),
                "note": "Initial inbound batch",
            },
        )

        GoodsReceiptItem.objects.update_or_create(
            goods_receipt=receipt,
            product=product_map["SP003"],
            batch=batch_map[("WH-HN", "SP003", "BOX-2026-02")],
            defaults={
                "quantity": 40,
                "unit_cost": Decimal("9200.00"),
                "note": "Second inbound batch",
            },
        )

    def seed_goods_issues(self, warehouse_map, product_map, batch_map):
        issue, _created = GoodsIssue.objects.update_or_create(
            issue_no="GI-0001",
            defaults={
                "warehouse": warehouse_map["WH-HN"],
                "customer_name": "Internal Store Replenishment",
                "reference_no": "SO-DEMO-001",
                "status": GoodsIssue.STATUS_POSTED,
                "note": "Outbound issue for trial usage",
            },
        )

        GoodsIssueItem.objects.update_or_create(
            goods_issue=issue,
            product=product_map["SP001"],
            batch=None,
            defaults={
                "quantity": 5,
                "unit_price": Decimal("1250000.00"),
                "note": "Issue scanners for branch usage",
            },
        )

    def seed_stock_transfers(self, warehouse_map, product_map, batch_map):
        transfer, _created = StockTransfer.objects.update_or_create(
            transfer_no="TR-0001",
            defaults={
                "source_warehouse": warehouse_map["WH-HN"],
                "destination_warehouse": warehouse_map["WH-HCM"],
                "status": StockTransfer.STATUS_COMPLETED,
                "note": "Rebalance boxes between warehouses",
            },
        )

        StockTransferItem.objects.update_or_create(
            transfer=transfer,
            product=product_map["SP003"],
            batch=batch_map[("WH-HN", "SP003", "BOX-2026-02")],
            defaults={
                "quantity": 15,
            },
        )

    def seed_stock_counts(self, warehouse_map, product_map, batch_map):
        count, _created = StockCount.objects.update_or_create(
            count_no="SC-0001",
            defaults={
                "warehouse": warehouse_map["WH-HCM"],
                "status": StockCount.STATUS_POSTED,
                "note": "Cycle count after transfer completion",
            },
        )

        StockCountItem.objects.update_or_create(
            stock_count=count,
            product=product_map["SP004"],
            batch=batch_map[("WH-HCM", "SP004", "GLV-2026-01")],
            defaults={
                "expected_quantity": 52,
                "counted_quantity": 50,
                "difference_quantity": -2,
                "note": "Two pairs marked damaged during count",
            },
        )

    def seed_stock_movements(self, warehouse_map, product_map, batch_map, inventory_map):
        receipt = GoodsReceipt.objects.get(receipt_no="GR-0001")
        issue = GoodsIssue.objects.get(issue_no="GI-0001")
        transfer = StockTransfer.objects.get(transfer_no="TR-0001")
        count = StockCount.objects.get(count_no="SC-0001")

        movements_data = [
            {
                "warehouse": warehouse_map["WH-HN"],
                "product": product_map["SP003"],
                "batch": batch_map[("WH-HN", "SP003", "BOX-2026-01")],
                "movement_type": StockMovement.MOVEMENT_IN,
                "quantity": 80,
                "reference_no": receipt.receipt_no,
                "reason_code": StockMovement.REASON_PURCHASE,
                "quantity_before": 0,
                "quantity_after": 80,
                "note": "Inbound boxes batch 1",
                "goods_receipt": receipt,
            },
            {
                "warehouse": warehouse_map["WH-HN"],
                "product": product_map["SP003"],
                "batch": batch_map[("WH-HN", "SP003", "BOX-2026-02")],
                "movement_type": StockMovement.MOVEMENT_IN,
                "quantity": 40,
                "reference_no": receipt.receipt_no,
                "reason_code": StockMovement.REASON_PURCHASE,
                "quantity_before": 80,
                "quantity_after": 120,
                "note": "Inbound boxes batch 2",
                "goods_receipt": receipt,
            },
            {
                "warehouse": warehouse_map["WH-HN"],
                "product": product_map["SP001"],
                "batch": None,
                "movement_type": StockMovement.MOVEMENT_OUT,
                "quantity": 5,
                "reference_no": issue.issue_no,
                "reason_code": StockMovement.REASON_SALE,
                "quantity_before": 20,
                "quantity_after": 15,
                "note": "Issue scanners for internal request",
                "goods_issue": issue,
            },
            {
                "warehouse": warehouse_map["WH-HN"],
                "product": product_map["SP003"],
                "batch": batch_map[("WH-HN", "SP003", "BOX-2026-02")],
                "movement_type": StockMovement.MOVEMENT_OUT,
                "quantity": 15,
                "reference_no": transfer.transfer_no,
                "reason_code": StockMovement.REASON_TRANSFER,
                "quantity_before": 135,
                "quantity_after": 120,
                "note": "Transfer boxes out from Hanoi",
                "stock_transfer": transfer,
            },
            {
                "warehouse": warehouse_map["WH-HCM"],
                "product": product_map["SP003"],
                "batch": batch_map[("WH-HCM", "SP003", "BOX-2026-03")],
                "movement_type": StockMovement.MOVEMENT_IN,
                "quantity": 15,
                "reference_no": transfer.transfer_no,
                "reason_code": StockMovement.REASON_TRANSFER,
                "quantity_before": 10,
                "quantity_after": 25,
                "note": "Transfer boxes in to HCM",
                "stock_transfer": transfer,
            },
            {
                "warehouse": warehouse_map["WH-HCM"],
                "product": product_map["SP004"],
                "batch": batch_map[("WH-HCM", "SP004", "GLV-2026-01")],
                "movement_type": StockMovement.MOVEMENT_ADJUST,
                "quantity": 50,
                "reference_no": count.count_no,
                "reason_code": StockMovement.REASON_STOCK_COUNT,
                "quantity_before": 52,
                "quantity_after": 50,
                "note": "Cycle count adjustment for gloves",
                "stock_count": count,
            },
            {
                "warehouse": warehouse_map["WH-HN"],
                "product": product_map["SP002"],
                "batch": None,
                "movement_type": StockMovement.MOVEMENT_IN,
                "quantity": 6,
                "reference_no": "INIT-SP002",
                "reason_code": StockMovement.REASON_INITIAL,
                "quantity_before": 0,
                "quantity_after": inventory_map[("WH-HN", "SP002")].quantity,
                "note": "Initial balance for label printers",
            },
            {
                "warehouse": warehouse_map["WH-HCM"],
                "product": product_map["SP001"],
                "batch": None,
                "movement_type": StockMovement.MOVEMENT_IN,
                "quantity": 8,
                "reference_no": "INIT-SP001-HCM",
                "reason_code": StockMovement.REASON_INITIAL,
                "quantity_before": 0,
                "quantity_after": inventory_map[("WH-HCM", "SP001")].quantity,
                "note": "Initial balance for HCM scanners",
            },
        ]

        for item in movements_data:
            lookup = {
                "warehouse": item["warehouse"],
                "product": item["product"],
                "movement_type": item["movement_type"],
                "reference_no": item["reference_no"],
                "note": item["note"],
            }
            defaults = {
                "batch": item.get("batch"),
                "serial_number": item.get("serial_number"),
                "goods_receipt": item.get("goods_receipt"),
                "goods_issue": item.get("goods_issue"),
                "stock_transfer": item.get("stock_transfer"),
                "stock_count": item.get("stock_count"),
                "quantity": item["quantity"],
                "reason_code": item["reason_code"],
                "quantity_before": item["quantity_before"],
                "quantity_after": item["quantity_after"],
            }
            StockMovement.objects.update_or_create(**lookup, defaults=defaults)

    def print_summary(self):
        self.stdout.write(self.style.SUCCESS("Warehouse demo data seeded successfully."))
        self.stdout.write(
            "Categories: {categories}, Suppliers: {suppliers}, Warehouses: {warehouses}, "
            "Products: {products}, Inventories: {inventories}, Batches: {batches}, "
            "Serials: {serials}, Receipts: {receipts}, Issues: {issues}, "
            "Transfers: {transfers}, Counts: {counts}, Movements: {movements}".format(
                categories=Category.objects.count(),
                suppliers=Supplier.objects.count(),
                warehouses=Warehouse.objects.count(),
                products=Product.objects.count(),
                inventories=Inventory.objects.count(),
                batches=ProductBatch.objects.count(),
                serials=SerialNumber.objects.count(),
                receipts=GoodsReceipt.objects.count(),
                issues=GoodsIssue.objects.count(),
                transfers=StockTransfer.objects.count(),
                counts=StockCount.objects.count(),
                movements=StockMovement.objects.count(),
            )
        )
        self.stdout.write("Sample QR product code: PRODUCT:SP001")
        self.stdout.write("Sample QR inventory code: INV:WH-HN:SP001")
        self.stdout.write("Sample document references: GR-0001 / GI-0001 / TR-0001 / SC-0001")