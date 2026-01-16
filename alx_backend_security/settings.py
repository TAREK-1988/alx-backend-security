INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "ip_tracking",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "ip_tracking.middleware.IPTrackingMiddleware",
]

CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
        "LOCATION": "ip-tracking-cache",
        "TIMEOUT": 60 * 60 * 24,
    }
}

IP_GEOLOCATION_API_KEY = ""
IP_GEOLOCATION_USERNAME = ""
IP_GEOLOCATION_EXTRA_PARAMS = {}

CELERY_BROKER_URL = "redis://localhost:6379/0"
CELERY_RESULT_BACKEND = "redis://localhost:6379/0"
CELERY_TIMEZONE = "Africa/Cairo"

CELERY_BEAT_SCHEDULE = {
    "detect-ip-anomalies-hourly": {
        "task": "ip_tracking.tasks.detect_ip_anomalies",
        "schedule": 60 * 60,
    }
}

