from django.core.validators import MinValueValidator
from django.db import models
from warehouse.models.base import AuditUserModel, TimeStampedModel
from warehouse.models.category import Category
from warehouse.models.supplier import Supplier

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

    @property
    def volume(self):
        return self.width * self.length * self.height