#!/usr/bin/env python3
from __future__ import division

import argparse
import collections
import statistics

import sim
import utils


def get_candidates(e):
    res = e['res']
    candidates = {}
    candidates['best'] = min(min(v['diff']['lines'] for v in vals) for vals in res.values())
    for k, v in res.items():
        if k.startswith('merge_') or k.startswith('mours_'):
            candidates['%s_best' % k] = min(d['diff']['lines'] for d in v)
            continue
        if k.startswith('topmost_'):
            k = k[len('topmost_'):]

        diffs = [obj['diff']['lines'] for obj in v]

        candidates['%s_1' % k] = diffs[0]
        if len(v) > 1:
            candidates['%s_2' % k] = diffs[1]
        if len(v) > 2:
            candidates['%s_last' % k] = diffs[-1]
        # TODO add median etc.        

    return candidates


def eval_results(experiments):
    metrics = list(map(get_candidates, experiments))
    all_ids = sorted(metrics[0].keys())

    print('Relative to best result (mean):')
    mean_vals = {
        metric_id: statistics.mean(m[metric_id] / m['best'] for m in metrics)
        for metric_id in all_ids
    }
    print(
        '\n'.join('%-25s: %5s' % (mid, mv)
        for mid, mv in sorted(mean_vals.items(), key=lambda t: (t[1], t[0]))))


    # TODO best strat by number
    # TODO best strat by average
    # TODO best strat by mean


def main():
    parser = argparse.ArgumentParser(
        'Print out overall statistics for stats')
    parser.parse_args()

    experiments = utils.read_data('experiments', dirname=sim.DIRNAME)
    eval_results(experiments)


if __name__ == '__main__':
    main()
