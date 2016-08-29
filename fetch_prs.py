#!/usr/bin/env python3

import argparse

import progress

import utils
import query


def fetch_prs(repo_dict, verbose):
    basename = utils.safe_filename(repo_dict['full_name'])
    if utils.data_exists(basename, dirname='prs/'):
        return
    else:
        if verbose:
            print('PRs of %s ...' % repo_dict['html_url'])
        pulls_url = repo_dict['pulls_url'].replace('{/number}', '') + '?state=all'
        if 'youtube-dl' not in repo_dict['name']:
            return
        print(pulls_url)
        print(list(query.paged(pulls_url)))
        return

        forks_query = query.paged(forks_url)
        if verbose:
            forks = utils.progress_list(forks_query, repo_dict['forks_count'])
        else:
            forks = list(forks_query)
        utils.write_data(basename, forks, dirname='prs/')


def main():
    parser = argparse.ArgumentParser('Download all pull requests')
    parser.add_argument('-v', '--verbose', action='store_true', help='Show detailed status')
    args = parser.parse_args()

    config = utils.read_config()
    ignored_repos = set(config.get('ignored_repos', []))

    utils.ensure_datadir('prs/')

    initials = utils.read_data('list')
    if not args.verbose:
        initials = progress.bar.Bar('Downloading PRs').iter(initials)
    for irepo in initials:
        if irepo['full_name'] in ignored_repos:
            continue
        fetch_prs(irepo, args.verbose)

if __name__ == '__main__':
    main()
