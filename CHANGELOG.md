# Changelog

## 1.0.0 — 2026-07-29

### Changed

- **Framework migration**: replaced Pyramid WSGI + `c2cwsgiutils` with FastAPI ASGI + `c2casgiutils`.
- **Web server**: replaced `gunicorn` + `waitress` with `uvicorn`.
- **Configuration**: environment variables are now centralized via `pydantic-settings` with the `REDIRECT__` prefix.
  - `REDIRECT_HOSTS` → `REDIRECT__REDIRECT_HOSTS`
  - `REDIRECT_PARAM` → `REDIRECT__REDIRECT_PARAM`
  - `LOG_LEVEL` → `REDIRECT__LOG_LEVEL`
  - Infrastructure settings (Sentry, Redis, Prometheus, route prefix, auth) are now managed by `c2casgiutils` with the `C2C__` prefix.
- **Dependencies**: removed `pyramid`, `pyramid-mako`, `cornice`, `gunicorn`, `c2cwsgiutils`, `setuptools`. Added `fastapi`, `uvicorn`, `c2casgiutils`, `pydantic-settings`, `httpx` (dev).
- **Tests**: migrated from Pyramid test infrastructure to `httpx.AsyncClient` with `ASGITransport`.
- **Entry point**: changed from `paste.app_factory` to `redirect:app` (FastAPI instance).

### Removed

- `development.ini`, `production.ini`, `testing.ini` configuration files.
- `gunicorn.conf.py` configuration file.
- `redirect/routes.py` (Pyramid routes).
- `redirect/pshell.py` (Pyramid shell setup).
- `CHANGES.txt` replaced by `CHANGELOG.md`.
