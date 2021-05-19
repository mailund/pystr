
init:
	pip install -r requirements.txt

test:
	pytest --cov=pystr tests

.PHONY: init test
