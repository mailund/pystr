
init:
	pip3 install -r requirements.txt
	pip3 install --editable .

check:
	python3 -m pycodestyle tests pystr
	python3 -m pydocstyle tests pystr
	python3 -m pylama tests pystr
	python3 -m bandit -s B101,B311 -r tests
	python3 -m bandit -s B101 -r pystr
	python3 -m pylint pystr
	python3 -m pylint tests/*.py
	mypy --strict -p pystr
	mypy --strict tests/*.py

test: check
	pytest --cov-report term-missing --cov=pystr tests

build:
	python3 -m build

install:
	python3 setup.py install

.PHONY: init check test build install
