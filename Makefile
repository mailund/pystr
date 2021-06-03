
init:
	pip3 install -r requirements.txt
	pip3 install --editable .

check:
	mypy --disallow-untyped-calls --disallow-untyped-defs --disallow-incomplete-defs -p pystr
	mypy --disallow-untyped-calls --disallow-untyped-defs --disallow-incomplete-defs -p pystr_vis
	mypy --disallow-untyped-calls --disallow-untyped-defs --disallow-incomplete-defs -p pystr_scripts
	mypy --disallow-untyped-calls --disallow-untyped-defs --disallow-incomplete-defs tests/*.py

test: check
	pytest --cov-report term-missing --cov=pystr --cov=pystr_vis --cov=pystr_scripts tests

build:
	python3 -m build

install:
	python3 setup.py install

# For this, use the kitty terminal: https://sw.kovidgoyal.net/kitty/
idot=dot -Tpng -Gbgcolor=black -Nfontcolor=white -Efontcolor=white -Efontsize=26 -Nfontsize=26 -Ncolor=white -Ecolor=white | kitty +kitten icat --align=left
display:
	@echo "Naive suffix tree construction, mississippi"
	@cd tests && python3 -c "from suffixtree_test import *; test_naive_to_dot()" | $(idot)

	@echo "McCreight suffix tree construction, mississippi"
	@cd tests && python3 -c "from suffixtree_test import *; test_mccreight_to_dot()" | $(idot)

	@echo "Simple trie (foo, bar, foobar, baz, barfoo) depth first"
	@cd tests && python3 -c "from trie_test import *; test_simple_to_dot(depth_first_trie)" | $(idot)

	@echo "Simple trie (foo, bar, foobar, baz, barfoo) breadth first"
	@cd tests && python3 -c "from trie_test import *; test_simple_to_dot(breadth_first_trie)" | $(idot)

	@echo "Simple trie (mississippi suffixes) depth first"
	@cd tests && python3 -c "from trie_test import *; test_mississippi_suffixes(depth_first_trie)" | $(idot)

	@echo "Simple trie (mississippi suffixes) breadth first"
	@cd tests && python3 -c "from trie_test import *; test_mississippi_suffixes(breadth_first_trie)" | $(idot)


.PHONY: init check test build install display
