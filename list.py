#!/usr/bin/env python3

import argparse

import common
import utils


def pluck_repo(r):
	return {
		k: common.pluck_val(getattr(r, '_' + k))
		for k in ['id', 'html_url', 'parent', 'forks_url']}


def main():
	parser = argparse.ArgumentParser('find initial repositories')
	parser.add_argument('-n', '--max-count', type=int, metavar='COUNT', dest='max_count', help='Number of repositories to search', default=1)
	args = parser.parse_args()

	config, g = common.connect()

	res = []
	for r in g.search_repositories('stars:>1', 'forks', 'desc')[:args.max_count]:
		res.append(pluck_repo(r))

	print('Found %d repositories' % len(res))

	utils.write_data('list', res)

if __name__ == '__main__':
	main()
