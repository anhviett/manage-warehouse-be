from django.core.validators import MinValueValidator
from django.db import models
from warehouse.models.base import AuditUserModel, TimeStampedModel
from warehouse.models.warehouse import Warehouse


class Shelf(TimeStampedModel, AuditUserModel):
    warehouse = models.ForeignKey(Warehouse, on_delete=models.CASCADE, related_name="shelves")
    code = models.CharField(max_length=50)
    zone = models.CharField(max_length=50, blank=True)
    max_volume = models.FloatField(help_text="cm3", validators=[MinValueValidator(0)])
    max_weight = models.FloatField(
        default=0,
        help_text="kg",
        validators=[MinValueValidator(0)],
    )
    width = models.FloatField(default=0, help_text="cm", validators=[MinValueValidator(0)])
    length = models.FloatField(default=0, help_text="cm", validators=[MinValueValidator(0)])
    height = models.FloatField(default=0, help_text="cm", validators=[MinValueValidator(0)])
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ["warehouse__code", "code"]
        constraints = [
            models.UniqueConstraint(
                fields=["warehouse", "code"],
                name="uniq_shelf_code_per_warehouse",
            )
        ]

    def __str__(self):
        return f"{self.warehouse.code} - {self.code}"

    @property
    def volume(self):
        if self.max_volume:
            return self.max_volume
        return self.width * self.length * self.height