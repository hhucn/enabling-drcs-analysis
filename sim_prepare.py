#!/usr/bin/env python3

import argparse
import collections
import functools
import random
import re

import sim_utils
import utils


def prepare(args, all_repos):
    rng = random.Random(42)
    n = args.config['sim']['experiment_count']
    tasks = []
    warnings = collections.defaultdict(list)

    def warnfunc(repo_dict, code, msg):
        basename = utils.safe_filename(repo_dict['full_name'])
        warnings[code].append(basename)
        if not args.quiet:
            print(msg)

    while len(tasks) < n:
        for i in range(len(tasks), n):
            rd = rng.choice(all_repos)
            seed = rng.randint(0, 2**64)
            params = {
                'config': args.config,
                'repo_dict': rd,
                'seed': seed,
                'idx': len(tasks),
                'n': n,
            }
            wf = functools.partial(warnfunc, rd)

            if sim_utils.check_experiment(params, wf):
                tasks.append(params)
                if not args.quiet:
                    print('%s: Added, now got %d/%d tasks!' % (rd['full_name'], len(tasks), n))

    return tasks, warnings


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
    tasks, warnings = prepare(args, all_repos)

    utils.write_data('sim_tasks', tasks)
    utils.write_data('sim_warnings', warnings)


if __name__ == '__main__':
    main()
