from django.core.cache import cache
from django.http import HttpResponseForbidden
from django.utils import timezone
from ipware import get_client_ip
from django.conf import settings

from ip_tracking.models import BlockedIP, RequestLog

try:
    from django_ip_geolocation.backends import IPGeolocationAPI
except Exception:
    IPGeolocationAPI = None


class IPTrackingMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        ip, _ = get_client_ip(request)
        ip_address = ip or "0.0.0.0"

        if BlockedIP.objects.filter(ip_address=ip_address).exists():
            return HttpResponseForbidden("Forbidden")

        country, city = self._get_geolocation(ip_address)

        RequestLog.objects.create(
            ip_address=ip_address,
            timestamp=timezone.now(),
            path=request.path,
            country=country,
            city=city,
        )

        return self.get_response(request)

    def _get_geolocation(self, ip_address):
        cache_key = f"ipgeo:{ip_address}"
        cached = cache.get(cache_key)
        if cached:
            return cached.get("country"), cached.get("city")

        country = None
        city = None

        if IPGeolocationAPI is not None:
            try:
                backend = IPGeolocationAPI(
                    api_key=getattr(settings, "IP_GEOLOCATION_API_KEY", "") or "",
                    username=getattr(settings, "IP_GEOLOCATION_USERNAME", "") or "",
                    extra_params=getattr(settings, "IP_GEOLOCATION_EXTRA_PARAMS", {}) or {},
                )
                location = backend.geolocate(ip_address)

                if location is not None:
                    loc_country = getattr(location, "country", None)
                    loc_city = getattr(location, "city", None)

                    if isinstance(loc_country, dict):
                        country = loc_country.get("name") or loc_country.get("code")
                    elif isinstance(loc_country, str):
                        country = loc_country

                    if isinstance(loc_city, str):
                        city = loc_city
            except Exception:
                country = None
                city = None

        cache.set(cache_key, {"country": country, "city": city}, 60 * 60 * 24)
        return country, city

