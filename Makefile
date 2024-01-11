## options
# based on https://tech.davis-hansson.com/p/make/
MAKEFLAGS += --warn-undefined-variables
MAKEFLAGS += --no-builtin-rules
SHELL := bash
.SHELLFLAGS := -eu -o pipefail -c
.ONESHELL:
.DEFAULT_GOAL := help
.DELETE_ON_ERROR:

## variables

ENVIRONMENT ?= dev
ARGS =
APP_NAME = example_app
SOURCE_DIR := src
TEST_DIR := tests

## formula

# based on https://marmelab.com/blog/2016/02/29/auto-documented-makefile.html
.PHONY: help
help:  ## print help message
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-30s\033[0m %s\n", $$1, $$2}'

## dependencies

.PHONY: deps-install-python
deps-install-python:
	poetry install
	pythno -m pip list

.PHONY: install-hooks
install-hooks:
	python -m pre_commit install --install-hooks

.PHONY: deps-install
deps-install: deps-install-python install-hooks ## install dependencies

.PHONY: deps-update
deps-update:
	poetry update
	poetry export --format requirements.txt --output requirements.txt --without-hashes
	python -m pre_commit autoupdate

requirements.txt: poetry.lock
	poetry export --format requirements.txt --output requirements.txt --without-hashes

requirements-dev.txt: poetry.lock
	poetry export --with dev --format requirements.txt --output requirements-dev.txt --without-hashes

## checks

.PHONY: format
format:
	python -m ruff check --fix .
	python -m ruff format .

.PHONY: lint
lint:
	python -m ruff check .
	python -m ruff format .
	python -m mypy $(SOURCE_DIR)

.PHONY: test
test:
	python -m pytest

.PHONY: run-ci
run-ci: deps-install-python lint test  ## run ci

## app

.PHONY: run-web-dev
run-web-dev:
	python -m ${APP_NAME}.gunicorn

.PHONY: run-web
run-web:  ## run python web
	python -m gunicorn -c python:${APP_NAME}.gunicorn_conf

.PHONY: run
run: run-web  ## run main python app

## docker-compose

.PHONY: dc-build
dc-build: requirements.txt  ## build app image
	docker compose build web_dev web_ci web

.PHONY: dc-push
dc-push:
	docker compose push web_dev web

.PHONY: dc-test
dc-ci:
	docker compose run --build --rm web_ci

.PHONY: dc-up
dc-up:  ## run app image
	docker compose up web_dev

.PHONY: dc-exec
dc-exec:
	docker compose exec web_dev /bin/bash

.PHONY: dc-stop
dc-stop:
	docker compose stop

.PHONY: dc-down
dc-down:
	docker compose down
