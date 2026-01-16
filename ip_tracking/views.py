from django.http import JsonResponse
from django.views.decorators.http import require_POST
from ratelimit.decorators import ratelimit


def _rate_by_auth(request):
    user = getattr(request, "user", None)
    if user is not None and getattr(user, "is_authenticated", False):
        return "10/m"
    return "5/m"


@require_POST
@ratelimit(key="ip", rate=_rate_by_auth, block=True)
def login_view(request):
    return JsonResponse({"status": "ok"})

