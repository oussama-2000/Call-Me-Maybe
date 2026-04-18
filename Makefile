
install:
	uv add -r requirements.txt

run:
	@uv run main.py

venv:
	uv venv

debug:
	python3 -m pdb 

clean:
	rm -rf __pycache__
	rm -rf mypy_cache

lint:
	flake8 .
	mypy . \
	--warn-return-any\
	--warn-unused-ignores\
	--ignore-missing-imports\
	--disallow-untyped-defs\
	--check-untyped-defs\

activate_uv:
	source $HOME/.local/bin/env

