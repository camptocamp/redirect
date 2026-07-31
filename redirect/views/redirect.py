# Copyright (c) 2022-2026, Camptocamp SA

"""Redirect view for FastAPI."""

import logging
import urllib
from typing import Any

import html_sanitizer
from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import HTMLResponse, RedirectResponse

from redirect.hosts import get_allowed_hosts
from redirect.settings import settings

_LOG = logging.getLogger(__name__)

router = APIRouter()

sanitizer = html_sanitizer.Sanitizer(
    {
        "tags": {
            "unexisting",
        },
        "attributes": {},
        "empty": set(),
        "separate": set(),
        "keep_typographic_whitespace": True,
    },
)


@router.get("/")
async def redirect_get(request: Request) -> Any:
    """Redirect to the URL specified in the 'came_from' parameter."""
    param_name = settings.redirect_param
    params = dict(request.query_params)
    if param_name not in params:
        message = [f"Missing &#x27;{param_name}&#x27; parameter", ""]
        for key, value in params.items():
            message.append(f"{sanitizer.sanitize(key)}: {sanitizer.sanitize(value)}")
        return HTMLResponse(
            status_code=400,
            content="\n".join(
                (
                    "<html>",
                    " <head>",
                    "  <title>400 Bad Request</title>",
                    " </head>",
                    " <body>",
                    "  <h1>400 Bad Request</h1>",
                    (
                        "  The server could not comply with the request since it is either "
                        "malformed or otherwise incorrect.<br/><br/>"
                    ),
                    "<br/>\n".join(message),
                    " </body>",
                    "</html>",
                ),
            ),
        )

    parsed_url = urllib.parse.urlparse(params[param_name])
    allowed_hosts = await get_allowed_hosts()
    if parsed_url.hostname not in allowed_hosts:
        _LOG.error("Host '%s' is not in: %s", parsed_url.hostname, ", ".join(allowed_hosts))
        msg = f"Host '{parsed_url.hostname}' is not allowed"
        raise HTTPException(status_code=400, detail=msg)

    query = dict(params)
    url_split = urllib.parse.urlsplit(query[param_name])
    new_query = dict(urllib.parse.parse_qsl(url_split.query))
    del query[param_name]
    new_query.update(query)
    return RedirectResponse(
        status_code=302,
        url=urllib.parse.urlunsplit(
            (
                url_split.scheme,
                url_split.netloc,
                url_split.path,
                urllib.parse.urlencode(new_query),
                url_split.fragment,
            ),
        ),
    )
