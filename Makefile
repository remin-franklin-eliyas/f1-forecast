.PHONY: help install lint format test fetch explore clean

help:  ## Show this help
	@grep -E '^[a-zA-Z_-]+:.*##' $(MAKEFILE_LIST) | \
		awk 'BEGIN {FS = ":.*## "}; {printf "  \033[36m%-14s\033[0m %s\n", $$1, $$2}'

install:  ## Install all dependencies (runtime + dev)
	pip install -r requirements.txt -r requirements-dev.txt
	pre-commit install

lint:  ## Run ruff lint checks
	ruff check .

format:  ## Auto-format and fix lint issues
	ruff format .
	ruff check --fix .

format-check:  ## Check formatting without modifying files (used in CI)
	ruff format --check .
	ruff check .

test:  ## Run the test suite
	pytest tests/ -v --tb=short

fetch:  ## Fetch latest F1 data (runs fetch_data.py)
	python data/fetch_data.py

explore:  ## Regenerate all visualisation charts
	python data/explore.py

clean:  ## Remove cache and build artefacts
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -delete
	rm -rf .pytest_cache .coverage htmlcov dist build *.egg-info
