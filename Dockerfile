FROM osgeo/gdal:ubuntu-small-3.5.0 AS base-all
LABEL maintainer Camptocamp "info@camptocamp.com"
SHELL ["/bin/bash", "-o", "pipefail", "-cux"]

RUN --mount=type=cache,target=/var/lib/apt/lists \
    --mount=type=cache,target=/var/cache,sharing=locked \
    apt-get update \
    && apt-get upgrade --assume-yes \
    && apt-get install --assume-yes --no-install-recommends python3-pip \
    && python3 -m pip install --disable-pip-version-check --upgrade pip

# Used to convert the locked packages by poetry to pip requirements format
# We don't directly use `poetry install` because it force to use a virtual environment.
FROM base-all as poetry

# Install Poetry
WORKDIR /tmp
COPY requirements.txt ./
RUN --mount=type=cache,target=/root/.cache \
    python3 -m pip install --disable-pip-version-check --requirement=requirements.txt

# Do the conversion
COPY poetry.lock pyproject.toml ./
RUN poetry export --output=requirements.txt \
    && poetry export --dev --output=requirements-dev.txt

# Base, the biggest thing is to install the Python packages
FROM base-all as base

# Fail on error on pipe, see: https://github.com/hadolint/hadolint/wiki/DL4006.
# Treat unset variables as an error when substituting.
# Print commands and their arguments as they are executed.
SHELL ["/bin/bash", "-o", "pipefail", "-cux"]

ENV SSL_CERT_FILE=/etc/ssl/certs/ca-certificates.crt

RUN --mount=type=cache,target=/var/lib/apt/lists \
    --mount=type=cache,target=/var/cache,sharing=locked \
    apt-get update \
    && apt-get upgrade --yes \
    && apt-get install --assume-yes --no-install-recommends python3-pip gcc libpq-dev python3-dev

RUN --mount=type=cache,target=/root/.cache \
    --mount=type=bind,from=poetry,source=/tmp,target=/poetry \
    python3 -m pip install --disable-pip-version-check --no-deps --requirement=/poetry/requirements.txt \
    && python3 -m compileall -q /usr/local/lib/python3.* \
    && apt-get remove --autoremove --assume-yes gcc

FROM base AS dev

RUN --mount=type=cache,target=/root/.cache \
    --mount=type=bind,from=poetry,source=/tmp,target=/poetry \
    python3 -m pip install --disable-pip-version-check --no-deps --requirement=/poetry/requirements-dev.txt

WORKDIR /app
COPY . ./
RUN --mount=type=cache,target=/root/.cache \
    python3 -m pip install --disable-pip-version-check --no-deps --editable=.

FROM base AS runtime

WORKDIR /app
COPY . ./
RUN --mount=type=cache,target=/root/.cache \
    python3 -m pip install --disable-pip-version-check --no-deps --editable=. \
    && python3 -m compileall -q /app/redirect

CMD [ "/usr/local/bin/gunicorn", "--paste=production.ini" ]

ARG GIT_HASH
ENV GIT_HASH=${GIT_HASH}

RUN c2cwsgiutils-genversion ${GIT_HASH}

# Default values for the environment variables
ENV \
    DEVELOPMENT=0 \
    LOG_TYPE=console \
    OTHER_LOG_LEVEL=WARNING \
    GUNICORN_LOG_LEVEL=WARNING \
    GUNICORN_ACCESS_LOG_LEVEL=INFO \
    C2CWSGIUTILS_LOG_LEVEL=WARNING \
    VISIBLE_ENTRY_POINT=/ \
    LOG_LEVEL=INFO
