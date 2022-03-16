import logging
import os
from typing import Any
from urllib.parse import urlparse

import pyramid.request
from cornice import Service
from pyramid.httpexceptions import HTTPBadRequest, HTTPFound

from redirect import ALLOWED_HOSTS

LOG = logging.getLogger(__name__)

param_name = os.environ.get("REDIRECT_PARAM", "came_from")

redirect_service = Service(
    name="redirect",
    description="The redirect service",
    path="/",
    cors_origins=(
        (f'https://{os.environ["VISIBLE_WEB_HOST"]}' if "VISIBLE_WEB_HOST" in os.environ else "*"),
    ),
)


@redirect_service.get()
def redirect_get(request: pyramid.request.Request) -> Any:
    if param_name not in request.GET:
        raise HTTPBadRequest("Missing '{param_name}' parameter")

    parsed_url = urlparse(request.GET[param_name])
    if parsed_url.hostname not in ALLOWED_HOSTS:
        raise HTTPBadRequest(f"Host '{parsed_url.hostname}' is not allowed")

    raise HTTPFound(request.GET[param_name])
