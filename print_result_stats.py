#!/usr/bin/env python3

import argparse
import collections
import statistics

import sim
import utils


def get_candidates(e):
    res = e['res']
    candidates = {}
    for k, v in res.items():
        if k.startswith('merge_') or k.startswith('mours_'):
            candidates['%s_best' % k] = min(d['diff']['lines'] for d in v)
            continue
        if k.startswith('topmost_'):
            k = k[len('topmost_'):]

        candidates['%s_1' % k] = v[0]['diff']['lines']
        if len(v) > 1:
            candidates['%s_2' % k] =  v[1]['diff']['lines']
        if len(v) > 2:
            candidates['_last'] =  v[-1]['diff']['lines']
        # TODO add median etc.        

    return candidates


def eval_results(experiments):
    metrics = list(map(get_candidates, experiments))

    ranking_spot = collections.defaultdict(collections.Counter)
    for m in metrics:
        ranking = sorted(m.keys(), key=lambda r: m[r])
        for spot, r in enumerate(ranking):
            ranking_spot[r][spot] += 1
    ranking_avgs = {r: statistics.mean(s.values()) for r, s in ranking_spot.items()}
    ranking_order = sorted(ranking_avgs.keys(), key=lambda r: ranking_avgs[r], reverse=True)
    print('Spots:\n%s' % '\n'.join(
        ' %d. %s(%dx1.)' % (i + 1, r, ranking_spot[r][0]) for i, r in enumerate(ranking_order)))

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
