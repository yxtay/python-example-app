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
	python -m pip list

.PHONY: deps-install
deps-install: deps-install-python  ## install dependencies
	python -m pre_commit install --install-hooks

.PHONY: deps-update
deps-update:
	poetry update
	python -m pre_commit autoupdate

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

.PHONY: run-dev
run-dev:
	python -m ${APP_NAME}.gunicorn

.PHONY: run
run:  ## run main python app
	python -m gunicorn -c python:${APP_NAME}.gunicorn_conf

## docker-compose

.PHONY: dc-build
dc-build:  ## build app image
	docker compose build app_dev app_ci app

.PHONY: dc-push
dc-push:
	docker compose push app_dev app

.PHONY: dc-test
dc-ci:
	docker compose run --build --rm app_ci

.PHONY: dc-up
dc-up:  ## run app image
	docker compose up app_dev

.PHONY: dc-exec
dc-exec:
	docker compose exec app_dev /bin/bash

.PHONY: dc-stop
dc-stop:
	docker compose stop

.PHONY: dc-down
dc-down:
	docker compose down
