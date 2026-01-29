
setup:
	uv sync

checks: lint test

lint:
	uv run ruff check .

format:
	uv run ruff check --fix .

test:
	uv run pytest

.PHONY: setup install checks lint format test
