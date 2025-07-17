import datetime

import redis

from django.conf import settings
from django.db import connection
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods


@csrf_exempt
@require_http_methods(["GET"])
def health_check(request):
    """
    Health check endpoint for monitoring and load balancers
    """
    status = {"status": "healthy", "timestamp": datetime.datetime.now().isoformat(), "services": {}}

    # Check database
    try:
        connection.ensure_connection()
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
        status["services"]["database"] = "healthy"
    except Exception as e:
        status["services"]["database"] = f"unhealthy: {str(e)}"
        status["status"] = "unhealthy"

    # Check Redis
    try:
        if hasattr(settings, "REDIS_URL"):
            r = redis.from_url(settings.REDIS_URL)
            r.ping()
            status["services"]["redis"] = "healthy"
        else:
            status["services"]["redis"] = "not configured"
    except Exception as e:
        status["services"]["redis"] = f"unhealthy: {str(e)}"
        status["status"] = "unhealthy"

    # Return appropriate status code
    status_code = 200 if status["status"] == "healthy" else 503

    return JsonResponse(status, status=status_code)
