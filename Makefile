run:
	./list.py -n 900
	./explore.py
	./list_prs.py
	./download.py
	./download_prs.py
	./gen_commit_lists.py -q

	./sim_prepare.py
	./sim_run.py

deps-sys:
	sudo apt update
	sudo apt install -y build-essential git python3-pip htop strace screen

deps: deps-sys
	sudo pip3 install progress requests gitpython

test:
	nosetests3 test/

lint:
	flake8 *.py test/

.PHONY: run test lint deps
