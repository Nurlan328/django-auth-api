"""URL routes for the accounts app."""
from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView

from . import views

urlpatterns = [
    path("auth/register", views.RegisterView.as_view(), name="register"),
    # JWT login (returns access + refresh tokens), rate-limited
    path("auth/login", views.LoginView.as_view(), name="login"),
    path("auth/refresh", TokenRefreshView.as_view(), name="refresh"),
    path("users/me", views.MeView.as_view(), name="me"),
    path("admin/users", views.UserListView.as_view(), name="admin-users"),
    path("admin/stats", views.StatsView.as_view(), name="admin-stats"),
]
