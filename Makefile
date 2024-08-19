.PHONY: build package-install test lint

build:
	poetry build

package-install:
	pip install --user dist/*.whl

test:
	pytest --cov=heclet_code tests/

lint:
	flake8 heclet_code tests