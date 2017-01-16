#!/usr/bin/env python3

import argparse
import random
import re

import sim_utils
import utils


def prepare(args, all_repos):
    rng = random.Random(42)
    n = args.config['sim']['experiment_count']
    tasks = []
    printfunc = (lambda x: x) if args.quiet else print

    while len(tasks) < n:
        for i in range(len(tasks), n):
            rd = rng.choice(all_repos)
            seed = rng.randint(0, 2**64)
            params = {
                'config': args.config,
                'repo_dict': rd,
                'seed': seed,
                'idx': i,
                'n': n,
            }

            if sim_utils.check_experiment(params, printfunc):
                tasks.append(params)
                printfunc('%s: Added, now got %d/%d tasks!' % (rd['full_name'], len(tasks), n))

    return tasks


def main():
    parser = argparse.ArgumentParser(
        'Determine which experiments to run')
    parser.add_argument(
        '-f', '--filter',
        metavar='REGEXP', type=re.compile,
        help='Filter by repository fullname (regular expressions)')
    parser.add_argument(
        '-q', '--quiet',
        action='store_true', default=False,
        help='Do not output that much chatter')
    args = parser.parse_args()

    config = utils.read_config()
    ignored_repos = set(config.get('ignored_repos', []))
    args.config = config

    def _should_visit(repo_dict):
        if repo_dict['full_name'] in ignored_repos:
            return False

        if args.filter and not args.filter.search(repo_dict['full_name']):
            return False

        return True

    all_repos = list(filter(_should_visit, utils.read_data('list')))
    tasks = prepare(args, all_repos)

    utils.write_data('sim_tasks', tasks)


if __name__ == '__main__':
    main()
