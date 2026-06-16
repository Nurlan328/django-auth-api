"""Database models for the accounts app."""
from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    """Custom user model.

    Extends Django's AbstractUser (which already provides username, password,
    email, is_staff, date_joined, etc.) and adds a `role` field for simple RBAC.
    Setting a custom user model from the very start is the recommended practice.
    """

    class Role(models.TextChoices):
        USER = "user", "User"
        ADMIN = "admin", "Admin"

    email = models.EmailField(unique=True)
    role = models.CharField(max_length=20, choices=Role.choices, default=Role.USER)
