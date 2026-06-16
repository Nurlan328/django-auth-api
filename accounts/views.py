"""DRF views — the thin HTTP layer (parse request, return response)."""
import logging

from django.contrib.auth import get_user_model
from django.core.cache import cache
from rest_framework import generics, permissions
from rest_framework.response import Response
from rest_framework.throttling import ScopedRateThrottle
from rest_framework.views import APIView
from rest_framework_simplejwt.views import TokenObtainPairView

from .permissions import IsAdminRole
from .serializers import RegisterSerializer, UserSerializer
from .tasks import send_welcome_email

User = get_user_model()
logger = logging.getLogger(__name__)

STATS_CACHE_KEY = "stats:users"
STATS_TTL_SECONDS = 30


class RegisterView(generics.CreateAPIView):
    """POST /auth/register — open to everyone."""

    queryset = User.objects.all()
    serializer_class = RegisterSerializer
    permission_classes = [permissions.AllowAny]

    def perform_create(self, serializer):
        user = serializer.save()
        # Queue a welcome email as a background task (Celery -> RabbitMQ).
        # If the broker is down, don't fail registration — just log it.
        try:
            send_welcome_email.delay(user.email, user.username)
        except Exception as exc:
            logger.warning("Failed to enqueue welcome email: %s", exc)


class LoginView(TokenObtainPairView):
    """POST /auth/login — JWT login, rate-limited (5/min) against brute force."""

    throttle_classes = [ScopedRateThrottle]
    throttle_scope = "login"


class MeView(generics.RetrieveAPIView):
    """GET /users/me — returns the current user (requires a valid token)."""

    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        return self.request.user


class UserListView(generics.ListAPIView):
    """GET /admin/users — admin only (403 for a regular user)."""

    queryset = User.objects.all().order_by("id")
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated, IsAdminRole]


class StatsView(APIView):
    """GET /admin/stats — user stats with caching (cache-aside). Admin only.

    The "source" field shows where the data came from: "cache" or "db".
    First request within the TTL hits the DB; later ones hit the cache.
    """

    permission_classes = [permissions.IsAuthenticated, IsAdminRole]

    def get(self, request):
        cached = cache.get(STATS_CACHE_KEY)
        if cached is not None:
            return Response({"source": "cache", **cached})

        data = {"total_users": User.objects.count()}
        cache.set(STATS_CACHE_KEY, data, timeout=STATS_TTL_SECONDS)
        return Response({"source": "db", **data})
