#!/usr/bin/env python3

import argparse
import os.path

import progress
import git

import download
import utils
import query
import list_prs



CANARY_DIRNAME = 'downloaded_prs'
DIRNAME = download.DIRNAME


def download_prs(repo_dict, verbose):
    basename = utils.safe_filename(repo_dict['full_name'])
    canary_path = utils.calc_filename(basename, dirname=CANARY_DIRNAME, suffix='')
    if os.path.exists(canary_path):
        return

    path = utils.calc_filename(basename, dirname=DIRNAME, suffix='')
    repo = git.repo.Repo(path)
    origin = repo.remotes.origin
    prs = utils.read_data(basename, list_prs.DIRNAME)

    if verbose:
        print('Fetching %d PRs from %s' % (len(prs), repo_dict['full_name']))

    branch_names = ['pull/%d/head' % pr['number'] for pr in prs]
    origin.fetch(branch_names)

    print('fetched! %s' % path)

    # TODO write canary once we're done


def main():
    parser = argparse.ArgumentParser('Download pull requests')
    parser.add_argument('-v', '--verbose', action='store_true', help='Show detailed status')
    args = parser.parse_args()

    utils.ensure_datadir(DIRNAME)

    utils.iter_repos(args, 'Downloading PRs', download_prs)

if __name__ == '__main__':
    main()
