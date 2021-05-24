
init:
	pip install -r requirements.txt

test:
	mypy -p pystr
	pytest --cov-report term-missing --cov=pystr tests

# For this, use the kitty terminal: https://sw.kovidgoyal.net/kitty/
idot=dot -Tpng -Gbgcolor=black -Nfontcolor=white -Efontcolor=white -Ncolor=white -Ecolor=white | kitty icat
display:
	@echo "Naive suffix tree construction, mississippi"
	@python3 -c "from suffixtree_test import *; test_naive_to_dot()" | $(idot)

	@echo "McCreight suffix tree construction, mississippi"
	@python3 -c "from suffixtree_test import *; test_mccreight_to_dot()" | $(idot)


.PHONY: init test display
