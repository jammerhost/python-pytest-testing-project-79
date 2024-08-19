build:
	poetry build

package-install:
	pip install --user dist/*.whl

test:
	poetry run pytest

check:
	poetry run flake8
	poetry run mypy hexlet_code/