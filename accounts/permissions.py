"""Custom DRF permissions."""
from rest_framework.permissions import BasePermission


class IsAdminRole(BasePermission):
    """Allows access only to authenticated users whose role == 'admin'.

    Note the difference in DRF:
      401 Unauthorized — not authenticated (no/invalid token)
      403 Forbidden    — authenticated, but this permission denies access
    """

    message = "Administrator privileges required"

    def has_permission(self, request, view):
        user = request.user
        return bool(user and user.is_authenticated and user.role == "admin")
