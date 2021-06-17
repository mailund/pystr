
init:
	pip3 install -r requirements.txt
	pip3 install --editable .

check:
	mypy --strict -p pystr
	mypy --strict tests/*.py

test: check
	pytest --cov-report term-missing --cov=pystr tests

build:
	python3 -m build

install:
	python3 setup.py install

.PHONY: init check test build install
