"""Celery background tasks for the accounts app."""
from celery import shared_task


@shared_task
def send_welcome_email(email: str, username: str) -> str:
    """"Send" a welcome email after registration.

    A real send (SMTP, SendGrid, etc.) would go here; for learning we just print.
    Run by a Celery worker in a separate process (the consumer):
        celery -A django_auth_api worker -l info --pool=solo
    (--pool=solo is needed on Windows.)
    """
    print(f"[email] Sending email to {email}: \"Welcome, {username}!\"")
    return f"sent:{email}"
