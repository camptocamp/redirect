# Redirect

Simple application that do an http redirect an URL to the `came_from` value of the query string.

This is used to have a common redirect url with OAuth2 authentication (e.g. with GitHub).

## Configuration

Environment variables are loaded via `pydantic-settings` with the `REDIRECT__` prefix:

| Variable                   | Default                    | Description                               |
| -------------------------- | -------------------------- | ----------------------------------------- |
| `REDIRECT__REDIRECT_HOSTS` | `/etc/redirect/hosts.yaml` | Path to the allowed hosts YAML file       |
| `REDIRECT__REDIRECT_PARAM` | `came_from`                | Query parameter name for the redirect URL |
| `REDIRECT__LOG_LEVEL`      | `INFO`                     | Application log level                     |

Infrastructure settings (Sentry, Redis, Prometheus, auth) are managed by `c2casgiutils` with the `C2C__` prefix.

## Contributing

Install the pre-commit hooks:

```bash
pip install pre-commit
pre-commit install --allow-missing-config
```
