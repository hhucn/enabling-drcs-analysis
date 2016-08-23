import json

from github import Github  # if this fails:  pip3 install pygithub


def read_config():
	config_fn = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'config.json')
	with open(config_fn) as config_f:
		return json.load(config_fn)


def connect():
	config = read_config()
	g = Github(config['user'], config['password'])

