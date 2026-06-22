# Devit

A social blogging REST API backend built with Django REST Framework. Users can create posts, follow others, like/save posts, comment with nested replies, and vote on comments.

## Tech Stack

| Layer | Technology |
|---|---|
| Language | Python 3.13 |
| Framework | Django 5.2 |
| API | Django REST Framework 3.16 |
| Authentication | JWT (cookie-based) + django-allauth |
| Database | PostgreSQL 15 |
| Cache/Broker | Redis 7 |
| Tasks | Celery 5.5 |
| API Docs | drf-spectacular (OpenAPI) |
| Containers | Docker + Docker Compose |

## Features

- **Authentication** — Registration with email verification, JWT tokens stored in HTTP-only cookies, login with username or email, password reset via email code
- **User Profiles** — Bio, avatar, banner, follower/following counts, follow/unfollow
- **Posts** — CRUD with title, slug, content, image, tags; Published/Pending status; full-text search
- **Likes** — Toggle like/unlike on posts with unique constraints
- **Saved Posts** — Bookmark/save posts for later
- **Comments** — Nested replies with like/dislike voting system
- **Tags** — Persian/English validated, auto-created, filterable
- **Media Uploads** — Image processing with auto-resize via django-imagekit
- **Standardized Responses** — Uniform `{ message, data }` format across all endpoints
- **API Documentation** — Swagger UI and ReDoc at `/api/schema/swagger-ui/` and `/api/schema/redoc/`

## Project Structure

```
devit/
├── AAA/                    # Django project configuration
│   ├── settings.py         # Main settings
│   ├── urls.py             # Root URL config
│   └── celery.py           # Celery app setup
├── accounts/               # User accounts app
│   ├── models.py           # User, Follow, PasswordResetCode
│   ├── views.py            # Auth, profile, follow views
│   ├── serializers.py      # User serializers
│   ├── authentication.py   # Custom JWT cookie auth
│   └── tasks.py            # Celery tasks (email)
├── posts/                  # Posts & social features app
│   ├── models.py           # Post, Tag, Comment, Like, Vote, SavedPost
│   ├── views.py            # Post, comment, tag views
│   └── serializers.py      # Post, comment serializers
├── core/                   # Shared utilities
│   ├── permissions.py      # Custom DRF permissions
│   ├── mixins.py           # StandardResponseMixin
│   └── exceptions.py       # Custom exception handler
├── media/                  # User uploads (avatars, posts)
├── docker-compose.yml      # Docker stack definition
├── Dockerfile              # Python 3.13-slim image
└── requirements.txt        # Python dependencies
```

## Installation

### Option A: Docker Compose (Recommended)

```bash
docker-compose up --build
```

This starts:

- **web** — Django API on port `8000`
- **db** — PostgreSQL 15 (data persisted in volume)
- **redis** — Redis 7 on port `6379`
- **worker** — Celery worker for async tasks

### Option B: Local Development

```bash
# Create virtual environment
python -m venv venv
venv\Scripts\activate          # Windows
# source venv/bin/activate    # Linux/Mac

# Install dependencies
pip install -r requirements.txt

# Set environment variables (or configure in settings.py)
export DB_NAME=postgres
export DB_USER=postgres
export DB_PASS=postgres
export DB_HOST=localhost
export DB_PORT=5432
export REDIS_HOST=localhost

# Run migrations
python manage.py migrate

# Create superuser
python manage.py createsuperuser

# Start dev server
python manage.py runserver
```

For local dev without PostgreSQL, uncomment the SQLite block in `AAA/settings.py` (lines 87-92) and comment out the PostgreSQL block (lines 94-103).

## API Endpoints

### Authentication — `/api/auth/`

| Method | Endpoint | Description |
|---|---|---|
| POST | `/api/auth/signup/` | Register new user |
| POST | `/api/auth/send_activation/` | Resend activation email |
| GET | `/api/auth/activate/<uidb64>/<token>/` | Activate account via email link |
| POST | `/api/auth/signin/` | Login (sets JWT cookies) |
| POST | `/api/auth/signout/` | Logout (clears cookies) |
| POST | `/api/auth/refresh_from_cookie/` | Refresh access token |
| POST | `/api/auth/password_reset_code/` | Request password reset code |
| POST | `/api/auth/password_reset/` | Reset password with code |
| GET/PATCH | `/api/auth/me/` | Get/update own profile |
| GET | `/api/auth/user/<username>/` | View any user's profile |
| GET | `/api/auth/search/` | Search users |
| POST/DELETE | `/api/auth/user/<username>/follow/` | Follow/unfollow user |
| GET | `/api/auth/user/<username>/followers/` | List user's followers |
| GET | `/api/auth/user/<username>/following/` | List who user follows |

### Posts — `/api/posts/`

| Method | Endpoint | Description |
|---|---|---|
| GET/POST | `/api/posts/` | List/create posts |
| GET/PUT/PATCH/DELETE | `/api/posts/<slug>/` | View/update/delete post |
| POST/DELETE | `/api/posts/<slug>/like/` | Like/unlike post |
| POST/DELETE | `/api/posts/<slug>/save/` | Save/unsave post |
| GET/POST | `/api/posts/<slug>/comments/` | List/create comments on post |
| GET/PUT/PATCH/DELETE | `/api/posts/comments/<pk>/` | View/update/delete comment |
| POST/DELETE | `/api/posts/comments/<pk>/vote/` | Vote on comment |
| GET | `/api/posts/comments/<pk>/replies/` | List replies to comment |
| GET | `/api/posts/user/<username>/` | List posts by user |
| GET | `/api/posts/saved/` | List saved posts |
| GET | `/api/posts/tags/` | List all tags |
| GET | `/api/posts/tags/<tag>/` | List posts by tag |

### Media & Docs

| Method | Endpoint | Description |
|---|---|---|
| POST | `/api/media/` | Upload media file |
| GET | `/api/schema/` | OpenAPI schema |
| GET | `/api/schema/swagger-ui/` | Swagger UI |
| GET | `/api/schema/redoc/` | ReDoc UI |

## Environment Variables

| Variable | Default | Description |
|---|---|---|
| `DB_NAME` | `postgres` | PostgreSQL database name |
| `DB_USER` | `postgres` | PostgreSQL username |
| `DB_PASS` | `postgres` | PostgreSQL password |
| `DB_HOST` | `db` | PostgreSQL host |
| `DB_PORT` | `5432` | PostgreSQL port |
| `REDIS_HOST` | `redis` | Redis host |
| `SECRET_KEY` | — | Django secret key (set in production) |
| `DEBUG` | `True` | Debug mode (set to `False` in production) |

## License

This project is open source. Add your preferred license here.
