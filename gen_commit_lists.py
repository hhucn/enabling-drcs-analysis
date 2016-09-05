#!/usr/bin/env python3

import argparse
import os.path
import time

import progress
import git

import download
import utils
import query
import list_prs


DIRNAME = 'commit_lists'


def gen_graphs(repo_dict, verbose):
    basename = utils.safe_filename(repo_dict['full_name'])
    if utils.data_exists(basename, DIRNAME):
        return

    path = utils.calc_filename(basename, dirname=download.DIRNAME, suffix='')
    repo = git.repo.Repo(path)
    origin = repo.remotes.origin
    prs = utils.read_data(basename, list_prs.DIRNAME)

    if verbose:
        print('Extracting commit list from %s' % (repo_dict['full_name']))

    print(repo.branches)

    # TODO: throw away gh-pages
    # TODO: iterate over all commits and store time
    # TODO: check time
    # TODO sort by time



def main():
    parser = argparse.ArgumentParser('Generate a list of all commits in a repository')
    parser.add_argument('-v', '--verbose', action='store_true', help='Show detailed status')
    args = parser.parse_args()

    utils.ensure_datadir(DIRNAME)

    utils.iter_repos(args, 'Extracting commits', gen_graphs)

if __name__ == '__main__':
    main()
