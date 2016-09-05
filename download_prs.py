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



CANARY_DIRNAME = 'downloaded_prs'


def download_prs(repo_dict, verbose):
    basename = utils.safe_filename(repo_dict['full_name'])
    if utils.data_exists(basename, CANARY_DIRNAME):
        return

    path = utils.calc_filename(basename, dirname=download.DIRNAME, suffix='')
    repo = git.repo.Repo(path)
    origin = repo.remotes.origin
    prs = utils.read_data(basename, list_prs.DIRNAME)

    if verbose:
        print('Fetching %d PRs from %s' % (len(prs), repo_dict['full_name']))

    branch_names = ['pull/%d/head:gha_pr_%d' % (pr['number'], pr['number']) for pr in prs]
    origin.fetch(branch_names)

    utils.write_data(basename, dirname=CANARY_DIRNAME, data={
        'timestamp': time.time(),
    })


def main():
    parser = argparse.ArgumentParser('Download pull requests')
    parser.add_argument('-v', '--verbose', action='store_true', help='Show detailed status')
    args = parser.parse_args()

    utils.ensure_datadir(CANARY_DIRNAME)

    utils.iter_repos(args, 'Downloading PRs', download_prs)

if __name__ == '__main__':
    main()
