from django.conf import settings
from django.core.cache import cache
from django.http import HttpResponseForbidden
from django.utils import timezone
from ipware import get_client_ip
import requests

from ip_tracking.models import BlockedIP, RequestLog

def _safe_ip(request):
    ip, _ = get_client_ip(request)
    return ip or "0.0.0.0"

def _normalize_path(path):
    if not path:
        return "/"
    return path if path.startswith("/") else f"/{path}"

def _get_geo_from_django_ipgeolocation(ip_address):
    try:
        from ipgeolocation import IpGeolocation
    except Exception:
        return None, None

    provider = getattr(settings, "IP_GEOLOCATION_PROVIDER", "ipinfo")
    api_key = getattr(settings, "IP_GEOLOCATION_API_KEY", "")
    username = getattr(settings, "IP_GEOLOCATION_USERNAME", "")
    extra_params = getattr(settings, "IP_GEOLOCATION_EXTRA_PARAMS", {}) or {}

    try:
        geo = IpGeolocation(provider=provider, api_key=api_key, username=username, **extra_params)
        data = geo.get(ip_address) or {}
        country = data.get("country_name") or data.get("country") or data.get("country_code")
        city = data.get("city")
        return country, city
    except Exception:
        return None, None

def _get_geo_from_ipinfo(ip_address):
    token = getattr(settings, "IPINFO_TOKEN", "") or ""
    if not token:
        return None, None
    try:
        r = requests.get(f"https://ipinfo.io/{ip_address}/json", params={"token": token}, timeout=3)
        if r.status_code != 200:
            return None, None
        data = r.json() or {}
        country = data.get("country")
        city = data.get("city")
        return country, city
    except Exception:
        return None, None

def _get_geolocation(ip_address):
    cache_key = f"ipgeo:{ip_address}"
    cached = cache.get(cache_key)
    if cached:
        return cached.get("country"), cached.get("city")

    country, city = _get_geo_from_django_ipgeolocation(ip_address)
    if not country and not city:
        country, city = _get_geo_from_ipinfo(ip_address)

    cache.set(cache_key, {"country": country, "city": city}, 60 * 60 * 24)
    return country, city

class IPTrackingMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        ip_address = _safe_ip(request)

        if BlockedIP.objects.filter(ip_address=ip_address).exists():
            return HttpResponseForbidden("Forbidden")

        path = _normalize_path(getattr(request, "path", "/"))
        country, city = _get_geolocation(ip_address)

        RequestLog.objects.create(
            ip_address=ip_address,
            timestamp=timezone.now(),
            path=path,
            country=country,
            city=city,
        )

        return self.get_response(request)
