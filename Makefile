clean-pyc:
	find . -name '*.pyc' -exec rm --force {} +
	find . -name '*.pyo' -exec rm --force {} +

lint:
	pylint *.py

run:
	python server.py

watch:
	find . -name \*.py | entr -r python server.py
