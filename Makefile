.PHONY: install
install:
	npm install
	poetry install
	pre-commit install
