# Copyright (c) 2022-2026, Camptocamp SA

"""FastAPI application entry point."""

import logging
import os
import re
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

import c2casgiutils
import c2casgiutils.config
import c2casgiutils.headers
import sentry_sdk
from fastapi import FastAPI, Request
from fastapi.responses import RedirectResponse
from prometheus_client import start_http_server
from prometheus_fastapi_instrumentator import Instrumentator
from starlette.middleware.cors import CORSMiddleware
from starlette.middleware.gzip import GZipMiddleware
from starlette.middleware.trustedhost import TrustedHostMiddleware

from redirect.views.redirect import router

_LOG = logging.getLogger(__name__)

if c2casgiutils.config.settings.sentry.dsn or "SENTRY_DSN" in os.environ:
    _LOG.info(
        "Sentry is enabled with URL: %s",
        c2casgiutils.config.settings.sentry.dsn or os.environ.get("SENTRY_DSN"),
    )
    sentry_sdk.init(
        **{
            k: v
            for k, v in c2casgiutils.config.settings.sentry.model_dump().items()
            if v is not None and k != "tags"
        },
    )

    for tag, value in c2casgiutils.config.settings.sentry.tags.items():
        sentry_sdk.set_tag(tag, value)


@asynccontextmanager
async def _lifespan(main_app: FastAPI) -> AsyncIterator[None]:
    _LOG.info("Starting the application")

    await c2casgiutils.startup(main_app)

    if c2casgiutils.config.settings.prometheus.port > 0:
        start_http_server(c2casgiutils.config.settings.prometheus.port)

    yield

    _LOG.info("Application stopped")


app = FastAPI(title="Redirect", lifespan=_lifespan)

app.add_middleware(TrustedHostMiddleware, allowed_hosts=["*"])
app.add_middleware(GZipMiddleware, minimum_size=1000)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

route_prefix = c2casgiutils.config.settings.route_prefix
route_prefix_escaped = re.escape(route_prefix[1:])
_LOG.info("Using route prefix: '%s'", route_prefix)

_ui_csp_headers: dict[str, str | list[str] | dict[str, str] | dict[str, list[str]] | None] = {
    "Content-Security-Policy": {
        "default-src": ["'self'"],
        "script-src-elem": ["'self'", c2casgiutils.headers.CSP_NONCE],
        "style-src-elem": ["'self'", c2casgiutils.headers.CSP_NONCE],
        "img-src": ["'self'", "data:"],
        "connect-src": ["'self'"],
    },
}

_ui_path_match = rf"^{route_prefix_escaped}$"

app.add_middleware(
    c2casgiutils.headers.ArmorHeaderMiddleware,
    headers_config={
        "http": {"headers": {"Strict-Transport-Security": None}}
        if c2casgiutils.config.settings.http
        else {"headers": {}},
        "ui": {
            "path_match": _ui_path_match,
            "headers": _ui_csp_headers,
            "status_code": 200,
        },
    },
)

if c2casgiutils.config.settings.proxy_headers.type != "none":
    app.add_middleware(
        c2casgiutils.headers.ForwardedHeadersMiddleware,
        trusted_hosts=c2casgiutils.config.settings.proxy_headers.trusted_hosts,
        headers_type=c2casgiutils.config.settings.proxy_headers.type,
    )


@app.get(f"{route_prefix}c2c")
async def redirect_c2c(request: Request) -> RedirectResponse:
    """Redirect to the mounted c2c app canonical path."""
    url = request.url
    redirect_url = url.path + "/"
    if url.query:
        redirect_url += f"?{url.query}"
    return RedirectResponse(url=redirect_url, status_code=307)


app.mount(f"{route_prefix}c2c", c2casgiutils.app)

instrumentator = Instrumentator(should_instrument_requests_inprogress=True)
instrumentator.instrument(app)

app.include_router(router, prefix=route_prefix.rstrip("/"))
