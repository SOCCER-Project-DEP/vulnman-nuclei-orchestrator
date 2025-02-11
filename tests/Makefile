SHELL := /bin/bash -O globstar

.PHONY: lint format

lint:
	@poetry run ruff check --show-source
	@poetry run ruff format --check
#	@python -m poetry run mypy --strict --pretty
	@poetry run deptry .

fix:
	@poetry run ruff format
	@poetry run ruff check --fix

