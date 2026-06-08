from django.db import models

from warehouse.models.base import AuditUserModel, TimeStampedModel

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