
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

# For this, use the kitty terminal: https://sw.kovidgoyal.net/kitty/
idot=dot -Tpng -Gbgcolor=black -Nfontcolor=white -Efontcolor=white -Efontsize=26 -Nfontsize=26 -Ncolor=white -Ecolor=white | kitty +kitten icat --align=left
display:
	@echo "Naive suffix tree construction, mississippi"
	@show-suffixtree --algo naive mississippi | $(idot)

	@echo "McCreight suffix tree construction, mississippi"
	@show-suffixtree --algo mccreight mississippi | $(idot)

	@echo "Simple (foo, bar, foobar, baz, barfoo) depth first"
	@show-trie foo bar foobar baz barfoo | $(idot)


.PHONY: init check test build install display
