#!/usr/bin/env python3

import argparse
import collections
import random
import time
import statistics


import sim
import utils


DIRNAME = 'compare_results'


def eval_results(experiments):
    for i, e in enumerate(experiments):
        print('[%d] %s' % (i, e['repo']))
        for k, results in sorted(e['res'].items()):
            results = sorted(results, key=lambda r: r['diff']['lines'])
            result_vals = [r['diff']['lines'] for r in results]
            best = results[0]
            second_str = (
                '(%2d)   %6d' % (results[1]['param'], results[1]['diff']['lines'])
                if len(results) > 1
                else '%13s' % '-')

            print(' %-24s: best(%2d) %6d   second%s   avg %6d   median %6d' % (
                '%s[%d]' % (k, len(results)),
                best['param'], best['diff']['lines'],
                second_str,
                statistics.mean(result_vals), statistics.median(result_vals)))

def main():
    parser = argparse.ArgumentParser(
        'Compare and display simulation results')
    args = parser.parse_args()

    experiments = utils.read_data('experiments', dirname=sim.DIRNAME)
    eval_results(experiments)


if __name__ == '__main__':
    main()
