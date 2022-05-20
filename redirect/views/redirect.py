import logging
import os
import urllib
from typing import Any

import pyramid.request
from cornice import Service
from pyramid.httpexceptions import HTTPBadRequest, HTTPFound

from redirect import get_allowed_hosts

LOG = logging.getLogger(__name__)

param_name = os.environ.get("REDIRECT_PARAM", "came_from")

redirect_service = Service(name="redirect", description="The redirect service", path="/")


@redirect_service.get()
def redirect_get(request: pyramid.request.Request) -> Any:
    if param_name not in request.GET:
        message = [f"Missing &#x27;{param_name}&#x27; parameter", ""]
        for key, value in request.GET.items():
            message.append(f"{key}: {value}")
        raise HTTPBadRequest(
            body="\n".join(
                (
                    "<html>",
                    " <head>",
                    "  <title>400 Bad Request</title>",
                    " </head>",
                    " <body>",
                    "  <h1>400 Bad Request</h1>",
                    "  The server could not comply with the request since it is either malformed or otherwise incorrect.<br/><br/>",
                    "<br/>\n".join(message),
                    " </body>",
                    "</html>",
                )
            )
        )

    parsed_url = urllib.parse.urlparse(request.GET[param_name])
    allowed_hosts = get_allowed_hosts()
    if parsed_url.hostname not in allowed_hosts:
        LOG.error("Host '%s' is not in: %s", parsed_url.hostname, ", ".join(allowed_hosts))
        raise HTTPBadRequest(f"Host '{parsed_url.hostname}' is not allowed")

    query = dict(request.GET)
    del query[param_name]
    raise HTTPFound(urllib.parse.urljoin(request.GET[param_name], f"?{urllib.parse.urlencode(query)}"))
