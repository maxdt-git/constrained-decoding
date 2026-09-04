VENV := /goinfre/$(USER)/call_me_maybe/.venv
UV_ENV := UV_PROJECT_ENVIRONMENT=$(VENV)

install:
	$(UV_ENV) uv add flake8
	$(UV_ENV) uv add mypy

run:
	$(UV_ENV) uv run python -m src

	

# debug:
# 	$(UV_ENV) -m pdb $(MAIN) $(CONFIG)

clean:
	$(UV_ENV) find . -type d -name "__pycache__" -exec rm -rf {} +
	$(UV_ENV) find . -type d -name ".mypy_cache" -exec rm -rf {} +

fclean: clean
	$(UV_ENV) rm -rf .venv

lint:
	$(UV_ENV) flake8 . --exclude=fly_venv
	$(UV_ENV) mypy . --warn-return-any --warn-unused-ignores \
	--ignore-missing-imports --disallow-untyped-defs --check-untyped-defs

lint-strict:
	$(UV_ENV) flake8 . --exclude=fly_venv
	$(UV_ENV) mypy . --warn-return-any --warn-unused-ignores \
	--ignore-missing-imports --disallow-untyped-defs --check-untyped-defs \
	--strict


.PHONY: venv install run debug clean fclean lint lint-strict
