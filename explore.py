#!/usr/bin/env python3

import argparse

import progress

import utils
import query


def explore(repo_dict, verbose, indent=0):
    basename = utils.safe_filename(repo_dict['full_name'])
    if utils.data_exists(basename, dirname='forks/'):
        forks = utils.read_data(basename, dirname='forks/')
    else:
        if verbose:
            print('%sForks of %s ...' % ('.' * indent, repo_dict['html_url']))
        utils.ensure_datadir('forks/')
        forks_url = '/repos/%s/forks?per_page=100' % repo_dict['full_name']
        forks_query = query.paged(forks_url)
        if verbose:
            forks = utils.progress_list(forks_query, repo_dict['forks_count'])
        else:
            forks = list(forks_query)
        utils.write_data(basename, forks, dirname='forks/')
    for f in forks:
        if f['forks_count'] > 0:
            explore(f, verbose, indent + 1)


def main():
    parser = argparse.ArgumentParser('find the whole network of repos')
    parser.add_argument('-v', '--verbose', action='store_true', help='Show detailed status')
    args = parser.parse_args()

    config = utils.read_config()
    ignored_repos = set(config.get('ignored_repos', []))

    initials = utils.read_data('list')
    if not args.verbose:
        initials = progress.bar.Bar('Exploring').iter(initials)
    for irepo in initials:
        if irepo['full_name'] in ignored_repos:
            continue
        explore(irepo, args.verbose)

if __name__ == '__main__':
    main()
