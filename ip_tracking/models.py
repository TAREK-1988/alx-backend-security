from django.db import models
from django.utils import timezone

class RequestLog(models.Model):
    ip_address = models.GenericIPAddressField()
    timestamp = models.DateTimeField(default=timezone.now, db_index=True)
    path = models.CharField(max_length=2048)
    country = models.CharField(max_length=128, null=True, blank=True)
    city = models.CharField(max_length=128, null=True, blank=True)

    def __str__(self):
        return f"{self.ip_address} {self.path} {self.timestamp.isoformat()}"

class BlockedIP(models.Model):
    ip_address = models.GenericIPAddressField(unique=True)

    def __str__(self):
        return self.ip_address

class SuspiciousIP(models.Model):
    ip_address = models.GenericIPAddressField(unique=True)
    reason = models.CharField(max_length=512)
    created_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"{self.ip_address} {self.reason}"
