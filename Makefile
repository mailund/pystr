
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

	@echo "Simple trie (foo, bar, foobar, baz, barfoo) depth first"
	@python3 -c "from trie_test import *; test_simple_to_dot(depth_first_trie)" | $(idot)

	@echo "Simple trie (foo, bar, foobar, baz, barfoo) breadth first"
	@python3 -c "from trie_test import *; test_simple_to_dot(breadth_first_trie)" | $(idot)

	@echo "Simple trie (mississippi suffixes) depth first"
	@python3 -c "from trie_test import *; test_mississippi_suffixes(depth_first_trie)" | $(idot)

	@echo "Simple trie (mississippi suffixes) breadth first"
	@python3 -c "from trie_test import *; test_mississippi_suffixes(breadth_first_trie)" | $(idot)


.PHONY: init test display
