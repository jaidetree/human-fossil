# Human Fossil

Django marketing site. Empty scaffold stage: no CMS content/pages yet.

## Setup

```sh
nix develop        # Python 3.13, uv, Postgres 18, Node 24
uv sync             # install Python deps
npm install         # install Tailwind/esbuild CLIs
npm run build:css   # compile static_src/css/input.css -> static/css/app.css
```

## Local Postgres

Local dev/CI use a Nix-provisioned Postgres, not a system install or a
Docker service container:

```sh
export PGDATA="$PWD/.pgdata"
export PGHOST="$PWD/.pgsocket"
export PGDATABASE=human_fossil_dev
export PGPORT=5433
mkdir -p "$PGHOST"
./scripts/db start    # init + start; ./scripts/db stop / status also available
export DATABASE_URL="postgres://localhost:$PGPORT/$PGDATABASE"
```

## Run

```sh
uv run python manage.py migrate
uv run python manage.py runserver
```

Visit [`localhost:8000`](http://localhost:8000).

## Test / lint / type-check

```sh
uv run pytest
uv run mypy .
uv run ruff format --check .
uv run ruff check .
```

## Media storage

CMS media (`WorkImage.image`, `Training.image`, `Resource.icon`,
`Resource.file`) is served from Cloudflare R2 (S3-compatible, via
`django-storages`) in production, and falls back to local filesystem
storage (`MEDIA_ROOT`) whenever the R2 env vars below aren't set — which is
the case in local dev and CI, so no credentials are required to run this
project locally.

Set these as Fly secrets for production (see ticket 18, production
cutover) — all four must be set together to activate R2:

| Env var                | Value                                                                           |
| ---------------------- | ------------------------------------------------------------------------------- |
| `R2_BUCKET_NAME`       | R2 bucket name                                                                  |
| `R2_ENDPOINT_URL`      | R2 S3-compatible endpoint, e.g. `https://<account_id>.r2.cloudflarestorage.com` |
| `R2_ACCESS_KEY_ID`     | R2 API token access key                                                         |
| `R2_SECRET_ACCESS_KEY` | R2 API token secret key                                                         |
| `R2_CUSTOM_DOMAIN`     | Optional. Public bucket hostname, e.g. `media.humanfossil.com` (no scheme)      |

Bind the custom domain to the bucket in Cloudflare (R2 → bucket → Settings →
Custom Domains). Without `R2_CUSTOM_DOMAIN`, media URLs point at the
authenticated S3 endpoint and won't load in browsers.

Site domain: set `ALLOWED_HOSTS=humanfossil.com,www.humanfossil.com` and
`CSRF_TRUSTED_ORIGINS=https://humanfossil.com,https://www.humanfossil.com`.

Static files (Tailwind CSS output) are unaffected — they're always served
via WhiteNoise from `STATIC_ROOT`, regardless of R2 configuration.

## Deploy

Hand-written `Dockerfile` (uv-based, `python:3.13-slim`), `fly.toml` targets
the staging Fly app `human-fossil-staging`. `fly deploy` requires
Fly credentials not available in every environment; see the ticket in
`.human-fossil-vault/Projects/django-migration/issues/Review/` for the manual
deploy steps.
