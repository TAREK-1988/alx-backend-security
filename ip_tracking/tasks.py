from celery import shared_task
from django.db.models import Count
from django.utils import timezone

from ip_tracking.models import RequestLog, SuspiciousIP


@shared_task
def detect_ip_anomalies():
    now = timezone.now()
    since = now - timezone.timedelta(hours=1)
    sensitive_paths = ["/admin", "/admin/", "/login", "/login/"]

    high_volume = (
        RequestLog.objects.filter(timestamp__gte=since)
        .values("ip_address")
        .annotate(total=Count("id"))
        .filter(total__gt=100)
    )

    for row in high_volume:
        ip = row["ip_address"]
        SuspiciousIP.objects.update_or_create(
            ip_address=ip,
            defaults={"reason": "Exceeded 100 requests/hour"},
        )

    sensitive_hits = (
        RequestLog.objects.filter(timestamp__gte=since)
        .filter(path__in=sensitive_paths)
        .values("ip_address")
        .annotate(total=Count("id"))
        .filter(total__gt=0)
    )

    for row in sensitive_hits:
        ip = row["ip_address"]
        SuspiciousIP.objects.update_or_create(
            ip_address=ip,
            defaults={"reason": "Accessed sensitive path"},
        )

    return {"high_volume": high_volume.count(), "sensitive": sensitive_hits.count()}

