run:
	#./list.py -n 900
	#./explore.py
	#./list_prs.py
	#./download.py
	./download_prs.py

deps:
	pip3 install progress requests gitpython

test:
	nosetests3 .

lint:
	flake8 .

.PHONY: run test lint deps
