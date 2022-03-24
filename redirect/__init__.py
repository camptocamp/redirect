import logging
import os

import c2cwsgiutils.db
import c2cwsgiutils.health_check
import yaml
from pyramid.config import Configurator

LOG = logging.getLogger(__name__)
ALLOWED_HOSTS = set()


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

        with open(
            os.environ.get("REDIRECT_HOSTS", "/etc/redirect/hosts.yaml"),
            encoding="utf-8",
        ) as config_file:
            hosts_config = yaml.load(config_file, Loader=yaml.SafeLoader)

        # Deeply find host to support any config from shared config operator.
        def fill_allowed_hosts(config):
            if isinstance(config, str):
                ALLOWED_HOSTS.add(config)
            elif isinstance(config, list):
                for elem in config:
                    fill_allowed_hosts(elem)
            elif isinstance(config, dict):
                for elem in config.values():
                    fill_allowed_hosts(elem)
            else:
                LOG.warning("Unknown type %s (%s)", type=type(config), config=config)

        fill_allowed_hosts(hosts_config)

        return config.make_wsgi_app()
