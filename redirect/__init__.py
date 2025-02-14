import datetime
import logging
import os
from pathlib import Path
from typing import Any

import c2cwsgiutils.db
import c2cwsgiutils.health_check
import yaml
from pyramid.config import Configurator

_LOG = logging.getLogger(__name__)
_ALLOWED_HOSTS: set[str] = set()
_ALLOWED_HOSTS_TIMESTAMP = 0.0


def main(global_config: Any, **settings: Any) -> Any:
    """Return a Pyramid WSGI application."""
    del global_config  # Unused.
    with Configurator(settings=settings) as config:
        config.include("pyramid_mako")
        config.include("cornice")
        config.include("c2cwsgiutils.pyramid")
        config.include(".routes")
        config.scan()
        # Initialize the health checks
        c2cwsgiutils.health_check.HealthCheck(config)

        return config.make_wsgi_app()


# Deeply find host to support any config from shared config operator.
def get_allowed_hosts() -> set[str]:
    """Get the allowed hosts from the configuration file."""
    global _ALLOWED_HOSTS_TIMESTAMP  # pylint: disable=global-statement  # noqa: PLW0603

    config_filename = Path(os.environ.get("REDIRECT_HOSTS", "/etc/redirect/hosts.yaml"))
    if config_filename.stat().st_mtime > _ALLOWED_HOSTS_TIMESTAMP:
        with config_filename.open(encoding="utf-8") as config_file:
            hosts_config = yaml.load(config_file, Loader=yaml.SafeLoader)
            _ALLOWED_HOSTS.clear()
            _fill_allowed_hosts(hosts_config)
            _ALLOWED_HOSTS_TIMESTAMP = config_filename.stat().st_mtime
    else:
        _LOG.debug(
            "No new host file, current date: %s, file date: %s",
            datetime.datetime.fromtimestamp(_ALLOWED_HOSTS_TIMESTAMP, tz=datetime.timezone.utc).strftime(
                "%d.%m.%Y %H:%M:%S",
            ),
            datetime.datetime.fromtimestamp(
                config_filename.stat().st_mtime,
                tz=datetime.timezone.utc,
            ).strftime("%d.%m.%Y %H:%M:%S"),
        )
    return set(_ALLOWED_HOSTS)


def _fill_allowed_hosts(config: Any) -> None:
    if isinstance(config, str):
        _ALLOWED_HOSTS.add(config)
    elif isinstance(config, list):
        for elem in config:
            _fill_allowed_hosts(elem)
    elif isinstance(config, dict):
        for elem in config.values():
            _fill_allowed_hosts(elem)
    else:
        _LOG.warning("Unknown type %s (%s)", type(config), config)
