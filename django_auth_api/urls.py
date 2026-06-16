"""Root URL configuration for the django_auth_api project."""
from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    # Django's own admin site is moved to /django-admin/ so that /admin/users
    # stays free for our API.
    path("django-admin/", admin.site.urls),
    path("", include("accounts.urls")),
]
