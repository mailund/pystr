
init:
	pip install -r requirements.txt

test:
	mypy -p pystr
	pytest --cov-report term-missing --cov=pystr tests

.PHONY: init test
