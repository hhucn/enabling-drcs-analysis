#!/usr/bin/env python3

import argparse

import common
import utils

import progress.bar


def explore(repo_dict):
	print('Forks of %s ...' % repo_dict['html_url'])
	utils.ensure_datadir('forks/')
	forks = utils.progress_list(
		common.paged('/repos/%s/forks?per_page=100' % repo_dict['full_name']),
		repo_dict['forks_count'])
	print(len(forks))
	die()


def main():
	parser = argparse.ArgumentParser('find the whole network of repos')
	args = parser.parse_args()

	config = utils.read_config()
	ignored_repos = set(config.get('ignored_repos', []))

	initials = utils.read_data('list')
	networks = []
	for irepo in initials:
		if irepo['full_name'] in ignored_repos:
			continue
		networks.append(explore(irepo))

if __name__ == '__main__':
	main()
