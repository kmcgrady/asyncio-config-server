clean-pyc:
	find . -name '*.pyc' -exec rm --force {} +
	find . -name '*.pyo' -exec rm --force {} +

lint:
	pylint *.py

run:
	python sanic_server.py

watch:
	find . -name \*.py | entr -r python sanic_server.py

test:
	pytest

test-with-coverage:
	py.test --cov=coverage .
