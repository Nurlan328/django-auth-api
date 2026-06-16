"""Register the User model in Django's built-in admin site.

Django's admin is one of its "batteries included" — a ready-made UI to manage
data. Here we also surface the custom `role` field. The admin lives at
/django-admin/ (we moved it so /admin/users stays free for the API).
"""
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import User


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    list_display = ("id", "username", "email", "role", "is_staff")
    fieldsets = UserAdmin.fieldsets + (("Role", {"fields": ("role",)}),)
