
INSTALL_DIR=$(HOME)/.config/blender/5.0/extensions/user_default/quickbake
ZIP_ARCHIVE_NAME=quickbake_0.0.0.zip

setup:
	uv sync

build_dev:
	@mkdir -p release/
	@cd src/quickbake && zip $(PWD)/release/$(ZIP_ARCHIVE_NAME) *

install:
	rm -rf $(INSTALL_DIR)/*
	cp -r src/quickbake/* $(INSTALL_DIR)/

run: install
	blender

checks: lint test

lint:
	uv run ruff format --check
	uv run ruff check .

format:
	uv run ruff format
	uv run ruff check --fix .

test:
	uv run pytest

.PHONY: setup build_dev install checks lint format test
