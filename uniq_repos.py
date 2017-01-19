#!/usr/bin/env python3

import argparse

import sim_utils
import utils


def main():
    parser = argparse.ArgumentParser('Print number of unique repositories in the experiments')
    parser.parse_args()

    results = sim_utils.read_results()
    repos = set(r['repo'] for r in results)
    newest_ts = max(r['ts'] for r in results)
    oldest_ts = min(r['ts'] for r in results)

    print('We performed %d experiments on %d different repositories.' % (len(results), len(repos)))
    print('Experiment time varied between %s and %s' % (oldest_ts, newest_ts))


if __name__ == '__main__':
    main()
