#!/usr/bin/env python3

import argparse
import os.path

import progress
import git

import utils
import query



DIRNAME = 'repos/'


def download(repo_dict, verbose):
    basename = utils.safe_filename(repo_dict['full_name'])
    path = utils.calc_filename(basename, dirname=DIRNAME)
    if os.path.exists(path):
        return

    tmp_path = path + '.tmp'

    #pulls = utils.read_data(basename, dirname='pulls/')
    #print(pulls[0].keys())

    if verbose:
        print('Downloading %s ...' % repo_dict['html_url'])
    git.Repo.clone_from(repo_dict['git_url'], tmp_path)



def main():
    parser = argparse.ArgumentParser('Download the repositories')
    parser.add_argument('-v', '--verbose', action='store_true', help='Show detailed status')
    args = parser.parse_args()

    config = utils.read_config()
    ignored_repos = set(config.get('ignored_repos', []))

    utils.ensure_datadir(DIRNAME)

    initials = utils.read_data('list')
    if not args.verbose:
        initials = progress.bar.Bar('Downloading repos').iter(initials)
    for irepo in initials:
        if irepo['full_name'] in ignored_repos:
            continue
        download(irepo, args.verbose)

if __name__ == '__main__':
    main()
