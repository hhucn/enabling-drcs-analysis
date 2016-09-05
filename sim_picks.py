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


def pick(config, repo):
    commit_list = utils.read_data(basename, gen_commit_list.DIRNAME)

    # Determine sensible times
    first_idx = round(config['cutoff'] * len(commit_list))
    first_time = commit_list[first_idx]['timestamp']
    last_time = commit_list[last_idx]['timestamp']

    rng = random.Random(0)
    for _ in range(config['experiments_per_repo']):
        ts = rng.randint(first_time, last_time)
        


def sim_pick(args, repo_dict):
    basename = utils.safe_filename(repo_dict['full_name'])

    if not utils.data_exists(basename, gen_commit_list.DIRNAME):
        print('No commit list for %s' % repo_dict['full_name'])
        return

    path = utils.calc_filename(basename, dirname=download.DIRNAME, suffix='')
    repo = git.repo.Repo(path)

    pick(args.config, repo)

    # TODO get start and end time
    # TODO cut a little bit from both (if possible)


def main():
    parser = argparse.ArgumentParser(
        'Pick random times and commits for experiments')
    utils.iter_repos(parser, DIRNAME, sim_pick)

if __name__ == '__main__':
    main()
