"""
URL configuration for grid project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.http import HttpResponse
from django.urls import include, path
from django.views import defaults as default_views
from drf_yasg import openapi
from drf_yasg.views import get_schema_view
from rest_framework import permissions

from grid.core.health import health_check


schema_view = get_schema_view(
    openapi.Info(
        title="OneSport API",
        default_version="v1",
        description="API documentation for OneSport HR/Recruiting Platform",
        terms_of_service="https://www.onesport.com/terms/",
        contact=openapi.Contact(email="api-support@onesport.com"),
        license=openapi.License(name="MIT License"),
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
)


def home(request):
    return HttpResponse("OneSport API - Welcome!")


urlpatterns = [
    # Core URLs
    path("admin/", admin.site.urls),
    path("", home, name="home"),
    path("health/", health_check, name="health-check"),
    # API Documentation
    path("swagger<format>/", schema_view.without_ui(cache_timeout=0), name="schema-json"),
    path("swagger/", schema_view.with_ui("swagger", cache_timeout=0), name="schema-swagger-ui"),
    path("docs/", schema_view.with_ui("swagger", cache_timeout=0), name="api-docs"),
    path("redoc/", schema_view.with_ui("redoc", cache_timeout=0), name="schema-redoc"),
    # API URLs
    path("api/auth/", include("grid.users.urls"), name="user-auth"),
    path("api/clients/", include("grid.clients.urls"), name="clients"),
    path("api/recruiters/", include("grid.recruiters.urls"), name="recruiters"),
    path("api/settings/", include("grid.site_settings.urls"), name="site_settings"),
    path("api/core/", include("grid.core.urls"), name="core"),
    path("api/jobs/", include("grid.jobs.urls"), name="jobs"),
    path("api/hires/", include("grid.hires.urls"), name="hires"),
    path("api/chats/", include("grid.chats.urls"), name="chats"),
]


if settings.DEBUG:
    # This allows the error pages to be debugged during development, just visit
    # these url in browser to see how these error pages look like.
    urlpatterns += [
        path(
            "400/",
            default_views.bad_request,
            kwargs={"exception": Exception("Bad Request!")},
        ),
        path(
            "403/",
            default_views.permission_denied,
            kwargs={"exception": Exception("Permission Denied")},
        ),
        path(
            "404/",
            default_views.page_not_found,
            kwargs={"exception": Exception("Page not Found")},
        ),
        path("500/", default_views.server_error),
    ]
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

    if "debug_toolbar" in settings.INSTALLED_APPS:
        import debug_toolbar

        urlpatterns = [path("__debug__/", include(debug_toolbar.urls))] + urlpatterns
