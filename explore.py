#!/usr/bin/env python3

import argparse

import utils
import query

DIRNAME = 'forks/'


def explore(args, repo_dict, indent=0):
    basename = utils.safe_filename(repo_dict['full_name'])
    if utils.data_exists(basename, dirname=DIRNAME):
        forks = utils.read_data(basename, dirname=DIRNAME)
    else:
        if args.verbose:
            print('%sForks of %s ...' % ('.' * indent, repo_dict['html_url']))

        forks_url = '/repos/%s/forks?per_page=100' % repo_dict['full_name']
        forks_query = query.paged(forks_url)
        if args.verbose:
            forks = utils.progress_list(forks_query, repo_dict['forks_count'])
        else:
            forks = list(forks_query)
        utils.write_data(basename, forks, dirname=DIRNAME)
    for f in forks:
        if f['forks_count'] > 0:
            explore(args, f, indent + 1)


def main():
    parser = argparse.ArgumentParser('find the whole network of repos')
    utils.iter_repos(parser, DIRNAME, explore)

if __name__ == '__main__':
    main()
