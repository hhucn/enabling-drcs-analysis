#!/usr/bin/env python3

import argparse
import random
import re

import sim_lib
import utils


DIRNAME = 'sim_tasks'


def prepare(args, all_repos):
    rng = random.Random(0)
    n = args.n
    tasks = []

    while len(tasks) < n:
        for i in range(len(tasks), n):
            rd = rng.choice(all_repos)
            seed = rng.random()
            params = {
                'config': args.config,
                'repo_dict': rd,
                'seed': seed,
                'idx': i,
                'n': n,
            }

            if sim_lib.check_experiment(params, print):
                tasks.push(params)


def main():
    parser = argparse.ArgumentParser(
        'Determine which experiments to run')
    parser.add_argument(
        '-f', '--filter',
        metavar='REGEXP', type=re.compile,
        help='Filter by repository fullname (regular expressions)')
    parser.add_argument(
        '-n', '--experiment-count', default=100,
        metavar='COUNT', type=int, dest='n',
        help='Number of experiments to perform (default: %(default)s)')
    args = parser.parse_args()

    config = utils.read_config()
    ignored_repos = set(config.get('ignored_repos', []))

    utils.ensure_datadir(DIRNAME)
    args.config = config

    def _should_visit(repo_dict):
        if repo_dict['full_name'] in ignored_repos:
            return False

        if args.filter and not args.filter.search(repo_dict['full_name']):
            return False

        return True

    all_repos = list(filter(_should_visit, utils.read_data('list')))
    tasks = []
    for e in prepare(args, all_repos):
        tasks.append(e)

    utils.write_data('tasks', tasks, dirname=DIRNAME)


if __name__ == '__main__':
    main()
