#!/usr/bin/env python3

import argparse
import time

import common


def format_duration(secs):
	if secs > 3600:
		return '%d hours' % (secs // 3600)
	if secs > 60:
		return '%d minutes' % (secs // 60)
	return '%d secs'


def main():
	parser = argparse.ArgumentParser('print current rate limit')
	args = parser.parse_args()

	_, data = common.query('/rate_limit')
	rate = data['rate']

	print('%d of %d remaining (reset in %s)' % (
		rate['remaining'], rate['limit'], format_duration(rate['reset'] - time.time())))

if __name__ == '__main__':
	main()
