###
# app configuration
# https://docs.gunicorn.org/en/stable/settings.html
###

import os

from c2cwsgiutils import get_config_defaults

bind = ":8080"

worker_class = "gthread"
workers = os.environ.get("GUNICORN_WORKERS", 2)
threads = os.environ.get("GUNICORN_THREADS", 10)

preload = "true"

accesslog = "-"
access_log_format = os.environ.get(
    "GUNICORN_ACCESS_LOG_FORMAT",
    '%(H)s %({Host}i)s %(m)s %(U)s?%(q)s "%(f)s" "%(a)s" %(s)s %(B)s %(D)s %(p)s',
)

###
# logging configuration
# https://docs.python.org/3/library/logging.config.html#logging-config-dictschema
###
logconfig_dict = {
    "version": 1,
    "root": {
        "level": os.environ["OTHER_LOG_LEVEL"],
        "handlers": [os.environ["LOG_TYPE"]],
    },
    "loggers": {
        "gunicorn.error": {"level": os.environ["GUNICORN_LOG_LEVEL"]},
        "gunicorn.access": {"level": os.environ["GUNICORN_ACCESS_LOG_LEVEL"]},
        "c2cwsgiutils": {"level": os.environ["C2CWSGIUTILS_LOG_LEVEL"]},
        "redirect": {"level": os.environ["LOG_LEVEL"]},
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "formatter": "generic",
            "stream": "ext://sys.stdout",
        },
        "json": {
            "class": "c2cwsgiutils.pyramid_logging.JsonLogHandler",
            "formatter": "generic",
            "stream": "ext://sys.stdout",
        },
    },
    "formatters": {
        "generic": {
            "format": "%(asctime)s [%(process)d] [%(levelname)-5.5s] %(message)s",
            "datefmt": "[%Y-%m-%d %H:%M:%S %z]",
            "class": "logging.Formatter",
        },
    },
}

raw_paste_global_conf = ["=".join(e) for e in get_config_defaults().items()]
