FROM osgeo/gdal:ubuntu-small-3.4.1 AS base
LABEL maintainer Camptocamp "info@camptocamp.com"

# Fail on error on pipe, see: https://github.com/hadolint/hadolint/wiki/DL4006.
# Treat unset variables as an error when substituting.
# Print commands and their arguments as they are executed.
SHELL ["/bin/bash", "-o", "pipefail", "-cux"]

ENV DEBIAN_FRONTEND=noninteractive \
    SSL_CERT_FILE=/etc/ssl/certs/ca-certificates.crt

# hadolint ignore=SC1091
RUN apt-get update && \
    apt-get install --assume-yes --no-install-recommends \
        python3-pip python3-wheel \
        gcc libpq-dev python3-dev && \
    apt-get clean && \
    rm --recursive --force /var/lib/apt/lists/*

COPY requirements.txt /tmp/
RUN python3 -m pip install --disable-pip-version-check --no-cache-dir --requirement=/tmp/requirements.txt && \
    rm --recursive --force /tmp/*

COPY Pipfile Pipfile.lock /tmp/

RUN cd /tmp && pipenv sync --system --clear && \
    rm --recursive --force /usr/local/lib/python3.*/dist-packages/tests/ /root/.cache/* && \
    python3 -m compileall -q /usr/local/lib/python3.* -x '/(pipenv)/' && \
    apt-get remove --autoremove --assume-yes gcc

FROM base AS lint

RUN cd /tmp && pipenv sync --system --clear --dev && \
    rm --recursive --force /usr/local/lib/python3.*/dist-packages/tests/ /root/.cache/*

WORKDIR /app
COPY . ./
RUN python3 -m pip install --disable-pip-version-check --no-cache-dir --editable=. && \
    prospector --output=pylint -X .


FROM base AS runtime

WORKDIR /app
COPY . ./
RUN python3 -m pip install --disable-pip-version-check --no-cache-dir --editable=. && \
    python3 -m compileall -q /app/redirect

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
    LOG_LEVEL=INFO
