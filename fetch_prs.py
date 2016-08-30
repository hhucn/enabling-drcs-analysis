#!/usr/bin/env python3

import argparse

import progress

import utils
import query


DIRNAME = 'pulls/'


def fetch_prs(repo_dict, verbose):
    basename = utils.safe_filename(repo_dict['full_name'])
    if utils.data_exists(basename, DIRNAME):
        return

    if verbose:
        print('PRs of %s ...' % repo_dict['html_url'])
    pulls_url = repo_dict['pulls_url'].replace('{/number}', '') + '?state=all&per_page=100'

    q = query.paged(pulls_url)
    if verbose:
        pulls = utils.progress_list(q)
    else:
        pulls = list(q)
    utils.write_data(basename, pulls, DIRNAME)


def main():
    parser = argparse.ArgumentParser('Download all pull requests')
    parser.add_argument('-v', '--verbose', action='store_true', help='Show detailed status')
    args = parser.parse_args()

    config = utils.read_config()
    ignored_repos = set(config.get('ignored_repos', []))

    utils.ensure_datadir(DIRNAME)

    initials = utils.read_data('list')
    if not args.verbose:
        initials = progress.bar.Bar('Downloading PRs').iter(initials)
    for irepo in initials:
        if irepo['full_name'] in ignored_repos:
            continue
        fetch_prs(irepo, args.verbose)

if __name__ == '__main__':
    main()
