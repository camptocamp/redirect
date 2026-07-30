"""Allowed hosts management."""

import datetime
import logging
from typing import Any

import yaml

from redirect.settings import settings

_LOG = logging.getLogger(__name__)
_ALLOWED_HOSTS: set[str] = set()
_ALLOWED_HOSTS_TIMESTAMP = 0.0


# Deeply find host to support any config from shared config operator.
async def get_allowed_hosts() -> set[str]:
    """Get the allowed hosts from the configuration file."""
    global _ALLOWED_HOSTS_TIMESTAMP  # pylint: disable=global-statement  # noqa: PLW0603

    config_filename = settings.redirect_hosts
    stat_result = await config_filename.stat()
    if stat_result.st_mtime > _ALLOWED_HOSTS_TIMESTAMP:
        hosts_config = yaml.load(
            await config_filename.read_text(encoding="utf-8"),
            Loader=yaml.SafeLoader,
        )
        _ALLOWED_HOSTS.clear()
        _fill_allowed_hosts(hosts_config)
        _ALLOWED_HOSTS_TIMESTAMP = stat_result.st_mtime
    else:
        _LOG.debug(
            "No new host file, current date: %s, file date: %s",
            datetime.datetime.fromtimestamp(_ALLOWED_HOSTS_TIMESTAMP, tz=datetime.UTC).strftime(
                "%d.%m.%Y %H:%M:%S",
            ),
            datetime.datetime.fromtimestamp(
                stat_result.st_mtime,
                tz=datetime.UTC,
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
