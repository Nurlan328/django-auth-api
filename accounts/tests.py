"""Tests for the accounts API (DRF APITestCase). Run: python manage.py test

The welcome-email Celery task is mocked (patched .delay) so tests need no broker.
"""
from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.core.cache import cache
from rest_framework.test import APITestCase

User = get_user_model()


class AuthTests(APITestCase):
    def setUp(self):
        # Clear the cache between tests so rate-limit counters and the stats
        # cache don't leak from one test into another.
        cache.clear()

    # --- helpers ---
    def register(self, username="alice", password="secret123"):
        return self.client.post(
            "/auth/register",
            {"username": username, "email": f"{username}@example.com", "password": password},
        )

    def login(self, username="alice", password="secret123"):
        r = self.client.post("/auth/login", {"username": username, "password": password})
        return r.data["access"]

    def authenticate(self, token):
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")

    def make_admin(self, username):
        user = User.objects.get(username=username)
        user.role = "admin"
        user.save()

    # --- registration ---
    @patch("accounts.views.send_welcome_email.delay")
    def test_register_success(self, _mock):
        r = self.register()
        self.assertEqual(r.status_code, 201)
        self.assertEqual(r.data["role"], "user")       # regular user by default
        self.assertNotIn("password", r.data)           # password never leaks out

    @patch("accounts.views.send_welcome_email.delay")
    def test_register_duplicate(self, _mock):
        self.register()
        r = self.register()                            # same username -> error
        self.assertEqual(r.status_code, 400)

    # --- login ---
    @patch("accounts.views.send_welcome_email.delay")
    def test_login_success(self, _mock):
        self.register()
        r = self.client.post("/auth/login", {"username": "alice", "password": "secret123"})
        self.assertEqual(r.status_code, 200)
        self.assertIn("access", r.data)

    @patch("accounts.views.send_welcome_email.delay")
    def test_login_wrong_password(self, _mock):
        self.register()
        r = self.client.post("/auth/login", {"username": "alice", "password": "WRONG"})
        self.assertEqual(r.status_code, 401)

    # --- protected /users/me ---
    def test_me_requires_token(self):
        r = self.client.get("/users/me")
        self.assertEqual(r.status_code, 401)           # no token, no access

    @patch("accounts.views.send_welcome_email.delay")
    def test_me_with_token(self, _mock):
        self.register()
        self.authenticate(self.login())
        r = self.client.get("/users/me")
        self.assertEqual(r.status_code, 200)
        self.assertEqual(r.data["username"], "alice")

    # --- role-based access /admin/users ---
    @patch("accounts.views.send_welcome_email.delay")
    def test_admin_forbidden_for_regular_user(self, _mock):
        self.register()
        self.authenticate(self.login())
        r = self.client.get("/admin/users")
        self.assertEqual(r.status_code, 403)           # logged in, but not an admin

    @patch("accounts.views.send_welcome_email.delay")
    def test_admin_allowed_for_admin(self, _mock):
        self.register(username="alice")
        self.register(username="bob")
        self.make_admin("alice")
        self.authenticate(self.login(username="alice"))
        r = self.client.get("/admin/users")
        self.assertEqual(r.status_code, 200)
        self.assertEqual(len(r.data), 2)               # alice and bob

    # --- background task (Celery / RabbitMQ) ---
    @patch("accounts.views.send_welcome_email.delay")
    def test_register_enqueues_welcome_email(self, mock_delay):
        self.register(username="alice")
        mock_delay.assert_called_once_with("alice@example.com", "alice")

    @patch("accounts.views.send_welcome_email.delay")
    def test_failed_register_does_not_enqueue(self, mock_delay):
        self.register(username="alice")
        mock_delay.reset_mock()
        r = self.register(username="alice")            # duplicate -> 400
        self.assertEqual(r.status_code, 400)
        mock_delay.assert_not_called()

    # --- caching (Redis in prod, LocMem in tests) ---
    @patch("accounts.views.send_welcome_email.delay")
    def test_stats_cache(self, _mock):
        self.register(username="alice")
        self.make_admin("alice")
        self.authenticate(self.login(username="alice"))

        r1 = self.client.get("/admin/stats")
        self.assertEqual(r1.status_code, 200)
        self.assertEqual(r1.data["source"], "db")      # first time — from the DB
        self.assertEqual(r1.data["total_users"], 1)

        r2 = self.client.get("/admin/stats")
        self.assertEqual(r2.data["source"], "cache")   # second time — from cache

    # --- rate limiting (DRF throttling) ---
    @patch("accounts.views.send_welcome_email.delay")
    def test_login_rate_limited(self, _mock):
        self.register()
        # limit = 5/min. The first 5 pass through (wrong password -> 401).
        for _ in range(5):
            r = self.client.post("/auth/login", {"username": "alice", "password": "WRONG"})
            self.assertEqual(r.status_code, 401)
        # the 6th request is throttled -> 429
        r = self.client.post("/auth/login", {"username": "alice", "password": "WRONG"})
        self.assertEqual(r.status_code, 429)
