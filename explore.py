#!/usr/bin/env python3

import argparse

import utils
import query


def explore(repo_dict):
    print('Forks of %s ...' % repo_dict['html_url'])
    utils.ensure_datadir('forks/')
    forks_url = '/repos/%s/forks?per_page=100' % repo_dict['full_name']
    forks = utils.progress_list(
        query.paged(forks_url), repo_dict['forks_count'])
    utils.write_data('forks/%s' % utils.safe_name(repo_dict['full_name']))
    for f in forks:
        if f['forks_count'] > 0:
            explore(f)


def main():
    parser = argparse.ArgumentParser('find the whole network of repos')
    parser.parse_args()

    config = utils.read_config()
    ignored_repos = set(config.get('ignored_repos', []))

    initials = utils.read_data('list')
    networks = []
    for irepo in initials:
        if irepo['full_name'] in ignored_repos:
            continue
        networks.append(explore(irepo))

if __name__ == '__main__':
    main()
