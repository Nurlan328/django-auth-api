# Auth API — a Django + DRF learning project

Registration, login, JWT tokens, and protected endpoints — the Django + Django
REST Framework twin of my [FastAPI auth API](https://github.com/Nurlan328/fastapi-auth-api), built to
compare the two approaches on the same feature set.

## Endpoints

| Method & path | Description |
|---|---|
| `POST /auth/register` | Register a new user |
| `POST /auth/login` | JWT login → `access` + `refresh` (rate-limited 5/min) |
| `POST /auth/refresh` | Refresh the access token |
| `GET /users/me` | Current user (requires a valid token) |
| `GET /admin/users` | List all users — admin only (403 otherwise) |
| `GET /admin/stats` | User stats, cached (cache-aside) — admin only |
| `/django-admin/` | Django's built-in admin UI |

## Structure

```
django-auth-api/
├── manage.py
├── docker-compose.yml          # postgres + redis + rabbitmq
├── .env.example                # copy to .env for the full stack
├── frontend/                   # React + Vite SPA (talks to this API)
├── django_auth_api/            # project package
│   ├── settings.py             # config via django-environ (.env)
│   ├── urls.py
│   └── celery.py               # Celery app (background tasks)
└── accounts/                   # the app
    ├── models.py               # custom User model (+ role)
    ├── serializers.py          # DRF serializers (validation / output)
    ├── permissions.py          # IsAdminRole (RBAC)
    ├── views.py                # register / login / me / admin / stats
    ├── tasks.py                # Celery welcome-email task
    ├── urls.py
    └── tests.py
```

## Running

### Quick start (no Docker)

Falls back to SQLite + in-memory cache — the same setup the tests use.

```bash
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
```

Open http://127.0.0.1:8000/users/me — DRF renders a browsable API UI.

### Full stack (Postgres + Redis + RabbitMQ)

```bash
# 1. copy .env.example to .env and uncomment the URLs
docker compose up -d
python manage.py migrate

# 2. terminal A — the Celery worker (queue consumer)
celery -A django_auth_api worker -l info --pool=solo   # --pool=solo is required on Windows

# 3. terminal B — the server
python manage.py runserver
```

Register a user and the worker prints the "sent" welcome email. Call
`/admin/stats` twice to see `"source": "db"` then `"source": "cache"`. A 6th
login within a minute returns `429 Too Many Requests`.

Create an admin for `/django-admin/`:

```bash
python manage.py createsuperuser
```

## Frontend

A React + Vite single-page app lives in `frontend/` — the same app as in the
FastAPI twin, only `VITE_API_BASE` differs (registration, login, profile, and an
admin view with the user list + cached stats).

```bash
cd frontend
npm install
npm run dev        # http://localhost:5173
```

Run the backend on http://127.0.0.1:8000 first (CORS already allows the dev
server). To unlock the admin panel, give a user the admin role:

```bash
python manage.py shell -c "from accounts.models import User; u = User.objects.get(username='alice'); u.role = 'admin'; u.save()"
```

<!-- Add a screenshot here, e.g.: ![screenshot](docs/screenshot.png) -->

## Tests

```bash
python manage.py test
```

The suite (12 tests) uses SQLite and an in-memory cache, and mocks the Celery
task, so it needs no Docker or external services.

## Stack

Python 3.14 · Django · Django REST Framework · SimpleJWT · Celery · RabbitMQ ·
Redis · PostgreSQL · Docker · django-environ · React + Vite

## Notes on the Django approach

Compared with the hand-wired FastAPI version, Django/DRF provides much of this
out of the box: password hashing (`create_user`), the ORM and migrations, the
admin UI, JWT endpoints (SimpleJWT), request throttling, and a cache framework.
You write less code but follow the framework's conventions.
