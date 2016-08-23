run:
	#./list.py -n 900
	./explore.py

test:
	nosetests3 .

lint:
	flake8 .

.PHONY: run test lint
