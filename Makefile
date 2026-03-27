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
	uv sync
	uv pip list

.PHONY: deps-install
deps-install: deps-install-python  ## install dependencies
	uvx pre-commit install --install-hooks

.PHONY: deps-update
deps-update:
	uv lock --upgrade
	uvx pre-commit-update

## checks

.PHONY: format
format:
	uvx ruff check --fix .
	uvx ruff format .

.PHONY: lint
lint:
	uvx ruff check .
	uvx ruff format .
	python -m mypy $(SOURCE_DIR)

.PHONY: test
test:
	python -m pytest

.PHONY: run-ci
run-ci: deps-install-python lint test  ## run ci

## app

.PHONY: run-dev
run-dev:
	uv run fastapi run src/${APP_NAME}/main.py --reload

.PHONY: run
run:  ## run main python app
	uv run fastapi run src/${APP_NAME}/main.py

## docker-compose

.PHONY: dc-build
dc-build:  ## build app image
	docker compose build app_dev app_ci app

.PHONY: dc-ci
dc-ci:
	docker compose run --build --rm app_ci

.PHONY: dc-up
dc-up:  ## run app image
	docker compose up app_dev

.PHONY: dc-exec
dc-exec:
	docker compose exec app_dev /bin/bash
