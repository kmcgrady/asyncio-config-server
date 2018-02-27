clean-pyc:
	find . -name '*.pyc' -exec rm --force {} +
	find . -name '*.pyo' -exec rm --force {} +

lint:
	pylint *.py

run:
	python sanic-server.py

watch:
	find . -name \*.py | entr -r python sanic-server.py
