# AutoKaraoke Makefile

.PHONY: install clean test run package venv

# Default Python interpreter
PYTHON = python3
VENV = venv
BIN = $(VENV)/bin

venv:
	$(PYTHON) -m venv $(VENV)
	$(BIN)/pip install --upgrade pip
	$(BIN)/pip install -e .

install: venv
	@echo "AutoKaraoke installed in virtual environment"

run: venv
	$(BIN)/autokaraoke

test: venv
	$(BIN)/pytest

clean:
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info
	rm -rf __pycache__/
	rm -rf .pytest_cache/
	rm -rf autokaraoke/__pycache__/
	rm -rf **/__pycache__/
	rm -rf **/**/__pycache__/
	find . -name '*.pyc' -delete

package: clean
	$(BIN)/pip install --upgrade build twine
	$(BIN)/python -m build
	@echo "Package built. Use '$(BIN)/python -m twine upload dist/*' to upload to PyPI"
