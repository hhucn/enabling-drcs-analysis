import os.path

import github  # if this fails:  pip3 install pygithub


import utils


def read_config():
	config_fn = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'config.json')
	return utils.read_json(config_fn)


def connect():
	config = read_config()
	g = github.Github(config['user'], config['password'])
	return config, g


def pluck_val(v):
	if isinstance(v, github.GithubObject._NotSetType):
		return None
	if isinstance(v, github.GithubObject._ValuedAttribute):
		return v.value
	return v