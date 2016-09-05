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
    commit_list_data = utils.read_data(basename, gen_commit_list.DIRNAME)
    commit_dict = {c['sha']: c for c in commit_list_data['commit_list']}

    def find_master_commit(ts):
        c = commit_dict[commit_list_data]
        while c['ts'] > ts:
            c = c['parents'][0]

        return c


    # Determine sensible times
    first_idx = round(config['cutoff'] * len(commit_list))
    first_time = commit_list[first_idx]['timestamp']
    last_time = commit_list[last_idx]['timestamp']

    rng = random.Random(0)
    for _ in range(config['experiments_per_repo']):
        ts = rng.randint(first_time, last_time)
        future_ts = ts + 24 * 60 * 60 * config['master_comparison_future_days']
        future_commit = find_master_commit(ts)


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
