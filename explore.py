#!/usr/bin/env python3

import argparse

import utils
import query


def explore(repo_dict, indent=0):
    basename = utils.safe_filename(repo_dict['full_name'])
    if utils.data_exists(basename, dirname='forks/'):
        return

    print('%sForks of %s ...' % ('.' * indent, repo_dict['html_url']))
    utils.ensure_datadir('forks/')
    forks_url = '/repos/%s/forks?per_page=100' % repo_dict['full_name']
    forks = utils.progress_list(
        query.paged(forks_url), repo_dict['forks_count'])
    utils.write_data(basename, forks, dirname='forks/')
    for f in forks:
        if f['forks_count'] > 0:
            explore(f, indent + 1)


def main():
    parser = argparse.ArgumentParser('find the whole network of repos')
    parser.parse_args()

    config = utils.read_config()
    ignored_repos = set(config.get('ignored_repos', []))

    initials = utils.read_data('list')
    for irepo in initials:
        if irepo['full_name'] in ignored_repos:
            continue
        explore(irepo)

if __name__ == '__main__':
    main()
