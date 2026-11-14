VENV ?= .venv
UV_ENV := UV_PROJECT_ENVIRONMENT=$(VENV)

install:
	$(UV_ENV) uv sync
	$(UV_ENV) uv add --dev flake8 mypy

run:
	$(UV_ENV) uv run python -m src

debug:
	$(UV_ENV) uv run python -m pdb -m src

clean:
	$(UV_ENV) find . -type d -name "__pycache__" -exec rm -rf {} +
	$(UV_ENV) find . -type d -name ".mypy_cache" -exec rm -rf {} +

fclean: clean
	$(UV_ENV) rm -rf .venv

lint:
	$(UV_ENV) uv run flake8 .
	$(UV_ENV) uv run mypy . --warn-return-any --warn-unused-ignores \
	--ignore-missing-imports --disallow-untyped-defs --check-untyped-defs

lint-strict:
	$(UV_ENV) uv run flake8 .
	$(UV_ENV) uv run mypy . --warn-return-any --warn-unused-ignores \
	--ignore-missing-imports --disallow-untyped-defs --check-untyped-defs \
	--strict


.PHONY: install run debug clean fclean lint lint-strict
