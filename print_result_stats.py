#!/usr/bin/env python3
from __future__ import division

import argparse
import collections
import re
import statistics

import sim
import utils


def get_candidates(e, diff_key):
    res = e['res']
    candidates = {}
    for k, v in res.items():
        m = re.match(r'^(?P<type>[a-z]+)_(?:greedy_)?(?P<crit>[a-z]+)$', k)
        if m:
            outk = '%(crit)s_%(type)s' % m.groupdict() if 'type' != 'topmost' else '%(crit)s'
        else:
            assert k in ('master',)
            outk = k

        if k.startswith('merge_') or k.startswith('mours_'):
            for pval in [2, 5, 10, 20, 50]:
                candidates['%s_%d' % (outk, pval)] = next(d['diff'][diff_key] for d in v if d['param'] == pval)
            continue

        diffs = [obj['diff'][diff_key] for obj in v]

        candidates['%s_1' % outk] = diffs[0]
        if len(v) > 1:
            candidates['%s_2' % outk] = diffs[1]
        if len(v) > 2:
            candidates['%s_%d' % (outk, len(v))] = diffs[-1]

    assert all(isinstance(v, int) for v in candidates.values())
    return candidates


def calc_rank(candidates):
    res = {}
    sorted_c = sorted(candidates.keys(), key=lambda k: candidates[k])
    it = iter(sorted_c)
    k = next(it)

    while True:
        affected_keys = []
        raw_val = candidates[k]
        while candidates[k] == raw_val:
            affected_keys.append(k)
            try:
                k = next(it)
            except StopIteration:
                k = None
                break

        start_idx = len(res)
        end_idx = start_idx + len(affected_keys) - 1
        for ak in affected_keys:
            res[ak] = (start_idx + end_idx) / 2

        if k is None:
            break

    return res


def eval_results(experiments, diff_key):
    results = [get_candidates(e, diff_key=diff_key) for e in experiments]
    ranks = list(map(calc_rank, results))

    strategy_ranks = {}
    for eranks in ranks:
        for ckey, crank in eranks.items():
            key_ranks = strategy_ranks.setdefault(ckey, [])
            key_ranks.append(crank)

    means = {mkey: statistics.mean(mranks) for mkey, mranks in strategy_ranks.items()}
    by_mean = sorted(means.keys(), key=lambda k: means[k])
    return {
        'experiment_count': len(experiments),
        'strategy_count': len(strategy_ranks),
        'diff_key': diff_key,
        'by_mean': by_mean,
        'means': means,
    }

def print_results(experiments):
    for diff_key in ('lines', 'len'):
        stats = eval_results(experiments, diff_key)
        print('%d experiments (evaluated by %s)' % (stats['experiment_count'], diff_key))
        print('%d strategies' % stats['strategy_count'])
        print('By mean:')
        for i, mkey in enumerate(stats['by_mean'], start=1):
            print('%2d. %-25s %.2f' % (i, mkey, stats['means'][mkey]))

    # How often No. 1?
    # Mean?
    # Median rank


def main():
    parser = argparse.ArgumentParser(
        'Print out overall statistics for stats')
    parser.parse_args()

    experiments = utils.read_data('experiments', dirname=sim.DIRNAME)
    print_results(experiments)


if __name__ == '__main__':
    main()
