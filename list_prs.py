#!/usr/bin/env python3

import argparse

import utils
import query


DIRNAME = 'pulls/'


def list_prs(args, repo_dict):
    basename = utils.safe_filename(repo_dict['full_name'])

    if args.verbose:
        print('PRs of %s ...' % repo_dict['html_url'])
    pulls_url = (
        repo_dict['pulls_url'].replace('{/number}', '') +
        '?state=all&per_page=100')

    q = query.paged(pulls_url)
    if args.verbose:
        pulls = utils.progress_list(q)
    else:
        pulls = list(q)
    utils.write_data(basename, pulls, DIRNAME)


def main():
    parser = argparse.ArgumentParser('List all pull requests')
    utils.iter_repos(parser, DIRNAME, list_prs)


if __name__ == '__main__':
    main()
