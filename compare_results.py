#!/usr/bin/env python3

import argparse
import collections
import random
import time


import sim
import utils


DIRNAME = 'compare_results'


def eval_results(experiments):
    for i, e in enumerate(experiments):
        print('[%d] %s' % (i, e['repo']))
        for k, results in sorted(e['res'].items()):
            best = min(results, key=lambda r: r['diff']['lines'])
            print(' %-20s: best(%2d) %6d out of %3d' % (k, best['param'], best['diff']['lines'], len(results)))

def main():
    parser = argparse.ArgumentParser(
        'Compare and display simulation results')
    args = parser.parse_args()

    experiments = utils.read_data('experiments', dirname=sim.DIRNAME)
    eval_results(experiments)


if __name__ == '__main__':
    main()
