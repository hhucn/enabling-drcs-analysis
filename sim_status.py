#!/usr/bin/env python3
from __future__ import division

import argparse
import itertools

import sim_utils


def ranges(sorted_nums):
    # From http://stackoverflow.com/a/4629241/35070
    for a, b in itertools.groupby(enumerate(sorted_nums), lambda tpl: tpl[1] - tpl[0]):
        b = list(b)
        yield b[0][1], b[-1][1]


def range_str(sorted_nums):
    if not sorted_nums:
        return '(nothing)'

    return ','.join(
        ('%d' % start) if start == end else ('%d-%d') % (start, end)
        for start, end in ranges(sorted_nums)
    )


def main():
    parser = argparse.ArgumentParser('Show status of simulation')
    parser.parse_args()

    results = sim_utils.read_results(include_errored=True)
    n = results[0]['params']['n']

    done = [
        i
        for i in range(n)
        if any(r['params']['idx'] == i for r in results)
    ]
    print('done: %s [%d/%d, %d%%]' % (range_str(done), len(done), n, int(round(100 * len(done) / n))))

    errored = [r['params']['idx'] for r in results if r.get('errored')]
    err_str = ','.join(map(str, errored)) if errored else 'nothing (fingers crossed)'
    print('errored: %s [%d/%d, %d%%]' % (err_str, len(errored), n, int(round(100 * len(errored) / n))))

    # TODO handle errored differently


if __name__ == '__main__':
    main()
