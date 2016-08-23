#!/usr/bin/env python3

import argparse

import utils


def main():
	parser = argparse.ArgumentParser('print generic statistics')
	args = parser.parse_args()

	repo_list = utils.read_data('list')
	for r in repo_list:
		print('%-80s - %d forks' % (r['html_url'], r['forks_count']))


if __name__ == '__main__':
	main()
