# fly launch's Django detector assumes pip/Poetry and doesn't understand
# uv.lock, so this image is hand-written around uv instead.
FROM python:3.13-slim AS base

# Pull the uv binary straight from Astral's distroless image rather than
# installing it via pip/curl.
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

WORKDIR /app

ENV UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy \
    PYTHONUNBUFFERED=1 \
    DJANGO_SETTINGS_MODULE=config.settings \
    PATH="/app/.venv/bin:$PATH"

# Install Python deps first so dependency layers cache independently of
# application code changes.
COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-install-project --no-dev

# Node is needed only at build time, to run the Tailwind CLI over
# static_src/ before collectstatic bakes the result into the image.
RUN apt-get update && apt-get install -y --no-install-recommends curl gnupg \
    && curl -fsSL https://deb.nodesource.com/setup_24.x | bash - \
    && apt-get install -y --no-install-recommends nodejs \
    && rm -rf /var/lib/apt/lists/*

COPY . .
RUN uv sync --frozen --no-dev

RUN npm ci && npm run build:css && rm -rf node_modules

# SECRET_KEY/DATABASE_URL aren't needed for collectstatic (no DB access,
# and STATIC_URL doesn't depend on secrets), but Django's settings module
# still imports cleanly without them since config/settings.py only reads
# what it needs lazily via django-environ defaults. Use the venv's own
# python directly (not `uv run`) so this doesn't trigger a dev-dependency
# resync at build or run time.
RUN python manage.py collectstatic --noinput

EXPOSE 8000

CMD ["gunicorn", "config.wsgi:application", "--bind", "0.0.0.0:8000"]
