"""Celery application for the project.

Celery is the standard way to run background/async tasks in the Django world
(the analogue of our standalone RabbitMQ worker in the FastAPI version).
"""
import os

from celery import Celery

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "django_auth_api.settings")

app = Celery("django_auth_api")

# Read CELERY_* options from Django settings (CELERY_BROKER_URL -> broker_url, etc.).
app.config_from_object("django.conf:settings", namespace="CELERY")

# Auto-discover tasks.py modules in installed apps.
app.autodiscover_tasks()
