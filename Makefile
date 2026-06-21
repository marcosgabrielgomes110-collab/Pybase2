.PHONY: install dev test build clean

install:
	pip install python-pybase

dev:
	pip install -e .

test:
	python -m pytest tests/ -v

test-all:
	python -m pytest tests/ --tb=long -v

build:
	python -m build

clean:
	rm -rf dist/ build/ *.egg-info
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true

publish:
	python -m build
	python -m twine upload dist/*

.PHONY: install dev test test-all build clean publish
