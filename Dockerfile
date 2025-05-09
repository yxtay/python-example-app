# hadolint global ignore=DL3008
# kics-scan disable=965a08d7-ef86-4f14-8792-4a3b2098937e
##
# base
##
FROM debian:stable-slim@sha256:88f88a2b8bd1873876a2ff15df523a66602aa57177e24b5f22064c4886ec398a AS base
LABEL maintainer="wyextay@gmail.com"

# set up user
ARG USER=user
ARG UID=1000
RUN useradd --create-home --shell /bin/false --uid ${UID} ${USER}

# set up environment
ARG APP_HOME=/work/app
ARG VIRTUAL_ENV=${APP_HOME}/.venv
ENV PATH=${VIRTUAL_ENV}/bin:${PATH} \
    PYTHONFAULTHANDLER=1 \
    PYTHONUNBUFFERED=1 \
    UV_PYTHON_INSTALL_DIR=/opt \
    VIRTUAL_ENV=${VIRTUAL_ENV}

WORKDIR ${APP_HOME}

RUN apt-get update && \
    apt-get upgrade --yes && \
    apt-get install --yes --no-install-recommends curl \
    && rm -rf /var/lib/apt/lists/*

##
# dev
##
FROM base AS dev

ARG DEBIAN_FRONTEND=noninteractive
COPY <<-EOF /etc/apt/apt.conf.d/99-disable-recommends
APT::Install-Recommends "false";
APT::Install-Suggests "false";
APT::AutoRemove::RecommendsImportant "false";
APT::AutoRemove::SuggestsImportant "false";
EOF

RUN apt-get update && \
    apt-get install --yes --no-install-recommends build-essential \
    && rm -rf /var/lib/apt/lists/*

ARG PYTHONDONTWRITEBYTECODE=1
ENV UV_LOCKED=1 \
    UV_NO_CACHE=1 \
    UV_NO_SYNC=1

# set up python
COPY --from=ghcr.io/astral-sh/uv:latest@sha256:87a04222b228501907f487b338ca6fc1514a93369bfce6930eb06c8d576e58a4 /uv /uvx /bin/
COPY .python-version pyproject.toml uv.lock ./
RUN uv sync --no-default-groups --no-install-project && \
    chown -R "${USER}:${USER}" "${VIRTUAL_ENV}" && \
    chown -R "${USER}:${USER}" "${APP_HOME}" && \
    uv pip list

# set up project
COPY src src
RUN uv sync --no-default-groups

EXPOSE 8000
ARG ENVIRONMENT=dev
ENV ENVIRONMENT=${ENVIRONMENT}
USER ${USER}
CMD ["gunicorn", "-c", "python:example_app.gunicorn_conf", "--reload"]

##
# ci
##
FROM dev AS ci

USER root
RUN uv sync && \
    uv pip list

COPY tests tests
COPY Makefile Makefile

USER ${USER}
RUN mkdir -p "${HOME}/.cache"
CMD ["make", "lint", "test"]

##
# compile
##
FROM dev AS compile

USER root
RUN apt-get update && \
    apt-get install --yes --no-install-recommends \
    binutils \
    patchelf \
    && rm -rf /var/lib/apt/lists/*

RUN uv pip install --no-cache-dir scons~=4.9 && \
    uv sync --group compile && \
    uv pip list

COPY main.py main.py
RUN pyinstaller --hidden-import example_app.main --onefile main.py && \
    staticx --strip dist/main /main

USER user
ENTRYPOINT [ "/dist/main" ]

##
# scratch
##
FROM scratch AS minimal

COPY --from=compile /tmp /tmp
COPY --from=compile /main /main

ENTRYPOINT [ "/main" ]

##
# prod
##
FROM base AS prod

# set up project
USER ${USER}
COPY --from=dev ${UV_PYTHON_INSTALL_DIR} ${UV_PYTHON_INSTALL_DIR}
COPY --from=dev ${VIRTUAL_ENV} ${VIRTUAL_ENV}
COPY --from=dev ${APP_HOME} ${APP_HOME}

EXPOSE 8000
ARG ENVIRONMENT=prod
ENV ENVIRONMENT=${ENVIRONMENT}
CMD ["gunicorn", "-c", "python:example_app.gunicorn_conf"]

HEALTHCHECK CMD ["curl", "-f", "http://localhost/"]
