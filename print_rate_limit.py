#!/usr/bin/env python3

import argparse
import time

import common


def format_duration(secs):
    if secs > 3600:
        return '%d hours' % (secs // 3600)
    if secs > 60:
        return '%d minutes' % (secs // 60)
    return '%d secs' % secs


def main():
    parser = argparse.ArgumentParser('print current rate limit')
    parser.parse_args()

    _, data = common.query('/rate_limit')
    now = time.time()

    for key, resource in sorted(data['resources'].items()):
        print('%d of %d %s remaining (reset in %s)' % (
            resource['remaining'],
            resource['limit'],
            key,
            format_duration(resource['reset'] - now)))


if __name__ == '__main__':
    main()
