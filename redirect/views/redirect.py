import logging
import os
import urllib
from typing import Any

import pyramid.request
from cornice import Service
from pyramid.httpexceptions import HTTPBadRequest, HTTPFound

from redirect import ALLOWED_HOSTS

LOG = logging.getLogger(__name__)

param_name = os.environ.get("REDIRECT_PARAM", "came_from")

redirect_service = Service(name="redirect", description="The redirect service", path="/")


@redirect_service.get()
def redirect_get(request: pyramid.request.Request) -> Any:
    if param_name not in request.GET:
        raise HTTPBadRequest(f"Missing '{param_name}' parameter")

    parsed_url = urllib.parse.urlparse(request.GET[param_name])
    if parsed_url.hostname not in ALLOWED_HOSTS:
        raise HTTPBadRequest(f"Host '{parsed_url.hostname}' is not allowed")

    query = dict(request.GET)
    del query[param_name]
    raise HTTPFound(urllib.parse.urljoin(request.GET[param_name], f"?{urllib.parse.urlencode(query)}"))
