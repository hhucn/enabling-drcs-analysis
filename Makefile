run:
	#./list.py -n 900
	./explore.py

test: lint

lint:
	flake8 .

.PHONY: run test lint
