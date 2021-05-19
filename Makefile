
init:
	pip install -r requirements.txt

test:
	pytest --cov-report term-missing --cov=pystr tests

.PHONY: init test
