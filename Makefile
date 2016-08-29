run:
	#./list.py -n 900
	./explore.py

deps:
	pip3 install progress requests

test:
	nosetests3 .

lint:
	flake8 .

.PHONY: run test lint deps
