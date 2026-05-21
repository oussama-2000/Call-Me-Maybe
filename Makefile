
install:
	@uv sync

run:
	@uv run python -m src

venv:
	uv venv

debug:
	python3 -m pdb 

clean:
	@find -name "__pycache__" -exec rm -rf {} +
	@rm -rf .mypy_cache

lint:
	flake8 .
	mypy . \
	--warn-return-any \
	--warn-unused-ignores \
	--ignore-missing-imports \
	--disallow-untyped-defs \
	--check-untyped-defs



