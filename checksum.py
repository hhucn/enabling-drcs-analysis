#!/usr/bin/env python3

import argparse
import json
import os
import hashlib

import utils


def dict_checksum(obj):
	j = json.dumps(obj, ensure_ascii=False, sort_keys=True)
	return hashlib.sha256(j.encode('utf-8')).hexdigest()


def print_checksum(args):
	print('config: %s' % dict_checksum(args.config))
	print('list: %s' % dict_checksum(utils.read_data('list')))


def main():
    parser = argparse.ArgumentParser('Show a checksum over the data')
    args = parser.parse_args()

    config = utils.read_config()
    args.config = config

    print_checksum(args)

if __name__ == '__main__':
	main()