run:
	./list.py -n 900
	./explore.py
	./list_prs.py
	./download.py
	./download_prs.py
	./gen_commit_lists.py -q
	./sim_picks.py -q

deps:
	sudo apt install -y git python3-pip htop strace screen
	pip3 install progress requests gitpython

test:
	nosetests3 test/

lint:
	flake8 *.py test/

.PHONY: run test lint deps
