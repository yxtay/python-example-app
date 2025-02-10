##
# base
##
FROM python:3.12-slim AS base
LABEL maintainer="wyextay@gmail.com"

# set up user
ARG USER=user
ARG UID=1000
RUN useradd --no-create-home --shell /bin/false --uid ${UID} ${USER}

# set up environment
ARG VIRTUAL_ENV=/work/venv
ENV PYTHONFAULTHANDLER=1 \
    PYTHONUNBUFFERED=1 \
    VIRTUAL_ENV=${VIRTUAL_ENV} \
    PATH=${VIRTUAL_ENV}/bin:${PATH}

ARG APP_HOME=/work/app
WORKDIR ${APP_HOME}

##
# dev
##
FROM base AS dev

ARG DEBIAN_FRONTEND=noninteractive
RUN --mount=type=cache,target=/var/cache/apt,sharing=locked \
    rm -f /etc/apt/apt.conf.d/docker-clean && \
    apt-get update && \
    apt-get install --no-install-recommends -y \
        build-essential \
        curl \
    && rm -rf /var/lib/apt/lists/*

ARG PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PIP_NO_CACHE_DIR=0 \
    PIP_NO_COMPILE=0 \
    PIP_NO_INPUT=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    UV_NO_CACHE=1

# set up python
COPY --from=ghcr.io/astral-sh/uv:0.5.29 /uv /uvx /bin/
COPY --chown=${USER}:${USER} pyproject.toml uv.lock ./
RUN --mount=type=cache,target=/root/.cache/uv \
    uv venv --seed ${VIRTUAL_ENV} && \
    uv sync --frozen --no-default-groups --no-install-project && \
    chown -R ${USER}:${USER} ${VIRTUAL_ENV} && \
    chown -R ${USER}:${USER} ${APP_HOME} && \
    uv pip list

# set up project
COPY --chown=${USER}:${USER} src src
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen --no-default-groups

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
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen && \
    chown -R ${USER}:${USER} ${VIRTUAL_ENV} && \
    uv pip list

USER ${USER}
COPY --chown=${USER}:${USER} tests tests
COPY --chown=${USER}:${USER} Makefile Makefile

CMD ["make", "lint", "test"]

##
# prod
##
FROM base AS prod

# set up project
USER ${USER}
COPY --from=dev --chown=${USER}:${USER} ${VIRTUAL_ENV} ${VIRTUAL_ENV}
COPY --from=dev --chown=${USER}:${USER} ${APP_HOME} ${APP_HOME}

EXPOSE 8000
ARG ENVIRONMENT=prod
ENV ENVIRONMENT=${ENVIRONMENT}
CMD ["gunicorn", "-c", "python:example_app.gunicorn_conf"]
