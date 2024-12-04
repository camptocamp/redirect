import logging
import os
import urllib
from typing import Any

import html_sanitizer
import pyramid.request
from cornice import Service
from pyramid.httpexceptions import HTTPBadRequest, HTTPFound

from redirect import get_allowed_hosts

_LOG = logging.getLogger(__name__)

param_name = os.environ.get("REDIRECT_PARAM", "came_from")

redirect_service = Service(name="redirect", description="The redirect service", path="/")


sanitizer = html_sanitizer.Sanitizer(
    {
        "tags": {
            "unexisting",
        },
        "attributes": {},
        "empty": set(),
        "separate": set(),
        "keep_typographic_whitespace": True,
    }
)


@redirect_service.get()
def redirect_get(request: pyramid.request.Request) -> Any:
    if param_name not in request.GET:
        message = [f"Missing &#x27;{param_name}&#x27; parameter", ""]
        for key, value in request.GET.items():
            message.append(f"{sanitizer.sanitize(key)}: {sanitizer.sanitize(value)}")
        raise HTTPBadRequest(
            body="\n".join(
                (
                    "<html>",
                    " <head>",
                    "  <title>400 Bad Request</title>",
                    " </head>",
                    " <body>",
                    "  <h1>400 Bad Request</h1>",
                    "  The server could not comply with the request since it is either "
                    "malformed or otherwise incorrect.<br/><br/>",
                    "<br/>\n".join(message),
                    " </body>",
                    "</html>",
                )
            )
        )

    parsed_url = urllib.parse.urlparse(request.GET[param_name])
    allowed_hosts = get_allowed_hosts()
    if parsed_url.hostname not in allowed_hosts:
        _LOG.error("Host '%s' is not in: %s", parsed_url.hostname, ", ".join(allowed_hosts))
        raise HTTPBadRequest(f"Host '{parsed_url.hostname}' is not allowed")

    query = dict(request.GET)
    url_split = urllib.parse.urlsplit(query[param_name])
    new_query = dict(urllib.parse.parse_qsl(url_split.query))
    del query[param_name]
    new_query.update(query)
    raise HTTPFound(
        urllib.parse.urlunsplit(
            (
                url_split.scheme,
                url_split.netloc,
                url_split.path,
                urllib.parse.urlencode(new_query),
                url_split.fragment,
            )
        )
    )
