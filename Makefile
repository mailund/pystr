
init:
	pip install -r requirements.txt

test:
	mypy -p pystr
	pytest --cov-report term-missing --cov=pystr tests

# For this, use the kitty terminal: https://sw.kovidgoyal.net/kitty/
idot=dot -Tpng -Gbgcolor=black -Nfontcolor=white -Efontcolor=white -Efontsize=26 -Nfontsize=26 -Ncolor=white -Ecolor=white | kitty +kitten icat --align=left
display:
	@echo "Naive suffix tree construction, mississippi"
	@python3 -c "from suffixtree_test import *; test_naive_to_dot()" | $(idot)

	@echo "McCreight suffix tree construction, mississippi"
	@python3 -c "from suffixtree_test import *; test_mccreight_to_dot()" | $(idot)

	@echo "Simple trie (foo, bar, foobar, baz, barfoo)"
	@python3 -c "from trie_test import *; test_simple_to_dot()" | $(idot)

.PHONY: init test display
