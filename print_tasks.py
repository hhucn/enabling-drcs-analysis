#!/usr/bin/env python3

import argparse

import utils

def print_tasks(_):
    tasks = utils.read_data('sim_tasks')
    for params in tasks:
        print('[%d/%d] %s (seed: %d)' % (
            params['idx'], params['n'],
            params['repo_dict']['full_name'],
            params['seed']))


def main():
    parser = argparse.ArgumentParser(
        'Print prepared experiment tasks')
    args = parser.parse_args()

    config = utils.read_config()
    args.config = config

    print_tasks(args)


if __name__ == '__main__':
    main()
