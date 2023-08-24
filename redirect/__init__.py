import datetime
import logging
import os

import c2cwsgiutils.db
import c2cwsgiutils.health_check
import yaml
from pyramid.config import Configurator

LOG = logging.getLogger(__name__)
_ALLOWED_HOSTS = set()
_ALLOWED_HOSTS_TIMESTAMP = 0


def main(global_config, **settings):
    """This function returns a Pyramid WSGI application."""
    del global_config  # Unused.
    with Configurator(settings=settings) as config:
        config.include("pyramid_mako")
        config.include("cornice")
        config.include(".routes")
        config.include("c2cwsgiutils.pyramid")
        config.scan()
        # Initialize the health checks
        c2cwsgiutils.health_check.HealthCheck(config)

        return config.make_wsgi_app()


# Deeply find host to support any config from shared config operator.
def get_allowed_hosts() -> set[str]:
    global _ALLOWED_HOSTS_TIMESTAMP  # pylint: disable=global-statement

    config_filename = os.environ.get("REDIRECT_HOSTS", "/etc/redirect/hosts.yaml")
    if _ALLOWED_HOSTS_TIMESTAMP < os.stat(config_filename).st_mtime:
        with open(config_filename, encoding="utf-8") as config_file:
            hosts_config = yaml.load(config_file, Loader=yaml.SafeLoader)
            _ALLOWED_HOSTS.clear()
            _fill_allowed_hosts(hosts_config)
            _ALLOWED_HOSTS_TIMESTAMP = os.stat(config_filename).st_mtime
    else:
        LOG.debug(
            "No new host file, current date: %s, file date: %s",
            datetime.datetime.fromtimestamp(_ALLOWED_HOSTS_TIMESTAMP).strftime("%d.%m.%Y %H:%M:%S"),
            datetime.datetime.fromtimestamp(os.stat(config_filename).st_mtime).strftime("%d.%m.%Y %H:%M:%S"),
        )
    return set(_ALLOWED_HOSTS)


def _fill_allowed_hosts(config) -> None:
    if isinstance(config, str):
        _ALLOWED_HOSTS.add(config)
    elif isinstance(config, list):
        for elem in config:
            _fill_allowed_hosts(elem)
    elif isinstance(config, dict):
        for elem in config.values():
            _fill_allowed_hosts(elem)
    else:
        LOG.warning("Unknown type %s (%s)", type=type(config), config=config)
