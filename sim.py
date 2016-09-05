#!/usr/bin/env python3

import argparse
import collections
import os.path
import random
import time

import progress
import git

import download
import utils
import query
import list_prs
import gen_commit_lists


DIRNAME = 'sim_results'
TMP_REPOS = 'sim_tmp'


def pick(config, basename, repo):
    utils.ensure_datadir(TMP_REPOS)

    commit_list_data = utils.read_data(basename, gen_commit_lists.DIRNAME)
    commit_list = commit_list_data['commit_list']
    commit_dict = {c['sha']: c for c in commit_list}

    def find_master_commit(ts):
        c = commit_dict[commit_list_data['master_head']]
        while c['ts'] > ts:
            c = commit_dict[c['parents'][0]]
        return c

    # Determine sensible times
    first_idx = round(config['cutoff_commits_first'] * len(commit_list))
    first_time = commit_list[first_idx]['ts']
    last_idx = round(config['cutoff_commits_last'] * len(commit_list))
    last_time = commit_list[last_idx]['ts']

    rng = random.Random(0)
    now = time.time()
    for i in range(config['experiments_per_repo']):
        ts = rng.randint(first_time, last_time)
        commit = find_master_commit(ts)
        future_ts = ts + 24 * 60 * 60 * config['master_comparison_future_days']
        future_commit = find_master_commit(future_ts)

        suffix = '-' + utils.timestr(now) + ('-%d' % i)
        tmp_repo_fn = utils.calc_filename(basename, dirname=TMP_REPOS, suffix=suffix)
        print(tmp_repo_fn)

        # TODO calculate diff

        # TODO determine tmp repo path
        # TODO check out into a repo where we can play around

        # TODO find one or more challengers


def sim_pick(args, repo_dict):
    basename = utils.safe_filename(repo_dict['full_name'])

    if not utils.data_exists(basename, gen_commit_lists.DIRNAME):
        if args.verbose or args.no_status:
            print('No commit list for %s' % repo_dict['full_name'])
        return

    path = utils.calc_filename(basename, dirname=download.DIRNAME, suffix='')
    repo = git.repo.Repo(path)

    pick(args.config, basename, repo)

    # TODO get start and end time
    # TODO cut a little bit from both (if possible)


def main():
    parser = argparse.ArgumentParser(
        'Pick random times and commits for experiments')
    utils.iter_repos(parser, DIRNAME, sim_pick)

if __name__ == '__main__':
    main()
