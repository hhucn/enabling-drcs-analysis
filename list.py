#!/usr/bin/env python3

import argparse

import query
import utils


def main():
    parser = argparse.ArgumentParser('find initial repositories')
    parser.add_argument(
        '-n', '--limit', type=int, metavar='COUNT', dest='limit',
        help='Number of repositories to search', default=1)
    args = parser.parse_args()

    res = utils.progress_list(query.paged('/search/repositories', params={
        'q': 'stars:>1',
        'sort': 'forks',
        'order': 'desc',
        'per_page': 100,
    }, limit=args.limit, get_items=lambda o: o['items']), args.limit)
    print('Found %d repositories' % len(res))

    utils.write_data('list', res)


if __name__ == '__main__':
    main()
