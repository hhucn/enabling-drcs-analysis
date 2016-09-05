#!/usr/bin/env python3

import argparse
import collections
import os.path
import random

import progress
import git

import download
import utils
import query
import list_prs
import gen_commit_list


DIRNAME = 'sim_picks'


def sim_pick(args, repo_dict):
    basename = utils.safe_filename(repo_dict['full_name'])

    if not utils.data_exists(basename, gen_commit_list.DIRNAME):
        print('No commit list for %s' % repo_dict['full_name'])
        return

    rng = random.Random(0)
    for _ in range(args.n):
        pass  # TODO call the rng

    # TODO get start and end time
    # TODO cut a little bit from both (if possible)


def main():
    parser = argparse.ArgumentParser(
        'Pick random times and commits for experiments')
    parser.add_argument(
        '-n', type=int, metavar='COUNT',
        help='Number of experiments per repository')
    utils.iter_repos(parser, DIRNAME, sim_pick)

if __name__ == '__main__':
    main()
