# hadolint global ignore=DL3008
FROM ghcr.io/astral-sh/uv:0.8.13@sha256:4de5495181a281bc744845b9579acf7b221d6791f99bcc211b9ec13f417c2853 AS uv

##
# base
##
FROM debian:stable-slim@sha256:8810492a2dd16b7f59239c1e0cc1e56c1a1a5957d11f639776bd6798e795608b AS base

# set up user
ARG USER=user
ARG UID=1000
RUN useradd --create-home --shell /bin/false --uid ${UID} ${USER}

# set up environment
ARG APP_HOME=/work/app
ARG DEBIAN_FRONTEND=noninteractive
ARG VIRTUAL_ENV=${APP_HOME}/.venv
ENV PATH=${VIRTUAL_ENV}/bin:${PATH} \
  PYTHONFAULTHANDLER=1 \
  PYTHONUNBUFFERED=1 \
  UV_LOCKED=1 \
  UV_NO_SYNC=1 \
  UV_PYTHON_DOWNLOADS=manual \
  UV_PYTHON_INSTALL_DIR=/opt/python \
  VIRTUAL_ENV=${VIRTUAL_ENV}

WORKDIR ${APP_HOME}

COPY <<-EOF /etc/apt/apt.conf.d/99-disable-recommends
APT::Install-Recommends "false";
APT::Install-Suggests "false";
APT::AutoRemove::RecommendsImportant "false";
APT::AutoRemove::SuggestsImportant "false";
EOF

RUN apt-get update && \
  apt-get upgrade --yes && \
  apt-get install --yes --no-install-recommends curl \
  && rm -rf /var/lib/apt/lists/*

##
# dev
##
FROM base AS dev

RUN apt-get update && \
  apt-get install --yes --no-install-recommends build-essential \
  && rm -rf /var/lib/apt/lists/*

ARG PYTHONDONTWRITEBYTECODE=1
ARG UV_NO_CACHE=1

# set up python
COPY --from=uv /uv /uvx /bin/
COPY .python-version pyproject.toml uv.lock ./
RUN uv python install && \
  uv sync --no-default-groups --no-install-project && \
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

USER ${USER}
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
