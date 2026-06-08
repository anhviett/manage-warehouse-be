from django.db import models
from .base import AuditUserModel, TimeStampedModel

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