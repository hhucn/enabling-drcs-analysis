#!/usr/bin/env python3
from __future__ import division

import argparse
import re
import statistics
import sys

import sim
import utils


IDXS = [0, 1, 4, 9, 49]
HUMAN_NAMES = {
    'master': 'master & 1 & pick',
    'ts': 'timestamp & {num} & pick',
    'depth': 'depth & {num} & pick',
    'size': 'size & {num} & pick',
    'author': 'author & {num} & pick',
    'ts_mours': 'timestamp & {num} & partial merge',
    'depth_mours': 'depth & {num} & partial merge',
    'size_mours': 'size & {num} & partial merge',
    'author_mours': 'author & {num} & partial merge',
    'ts_merge': 'timestamp & {num} & merged',
    'depth_merge': 'depth & {num} & merged',
    'size_merge': 'size & {num} & merged',
    'author_merge': 'author & {num} & merged',
    'topmost_random': 'random & 1 & pick',
    'random_merge': 'random & {num} & merged',
    'random_mours': 'random & {num} & partial merge',
}


def get_candidates(e, diff_idx, diff_key):
    res = e['res']
    candidates = {}
    for k, v in res.items():
        m = re.match(r'^(?P<type>[a-z]+)_(?:greedy_)?(?P<crit>[a-z]+)$', k)
        if m:
            if m.group('type') == 'topmost':
                outk = m.group('crit')
            else:
                outk = '%(crit)s_%(type)s' % m.groupdict()
        else:
            assert k in ('master',)
            outk = k

        if k.startswith('merge_') or k.startswith('mours_'):
            for pval in [2, 5, 10, 20, 50]:
                candidates['%s_%d' % (outk, pval)] = next(
                    d['diffs'][diff_idx][diff_key] for d in v if d['param'] == pval)
            continue
        if k == 'topmost_random':
            candidates['%s_0' % (k)] = next(d['diffs'][diff_idx][diff_key] for d in v)
            continue

        diffs = [obj['diffs'][diff_idx][diff_key] for obj in v]

        for idx in IDXS:
            if len(v) > idx:
                candidates['%s_%d' % (outk, idx+1)] = diffs[idx]

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


def eval_results(experiments, diff_idx, diff_key):
    results = [get_candidates(e, diff_idx=diff_idx, diff_key=diff_key) for e in experiments]
    ranks = list(map(calc_rank, results))

    strategy_ranks = {}
    for eranks in ranks:
        for ckey, crank in eranks.items():
            key_ranks = strategy_ranks.setdefault(ckey, [])
            key_ranks.append(crank)

    means = {mkey: statistics.mean(mranks) for mkey, mranks in strategy_ranks.items()}
    by_mean = sorted(means.keys(), key=lambda k: means[k])

    medians = {mkey: statistics.median(mranks) for mkey, mranks in strategy_ranks.items()}
    by_median = sorted(medians.keys(), key=lambda k: medians[k])

    return {
        'experiment_count': len(experiments),
        'strategy_count': len(strategy_ranks),
        'diff_key': diff_key,
        'by_mean': by_mean,
        'means': means,
        'by_median': by_median,
        'medians': medians,
    }


def print_results(args, experiments):
    idx = next(i for i, f in enumerate(experiments[0]['futures']) if f['days'] == args.days)

    all_stats = {}
    for diff_key in ('lines', 'len'):
        all_stats[diff_key] = eval_results(experiments, idx, diff_key)

    if args.latex:
        print('\\begin{tabular}[here]{lrl|rr|rr}')
        print('Criterion & Top & Strategy & \multicolumn{2}{c|}' +
              '{$\\overline{\mbox{pos. by lines}}$} & ' +
              '\multicolumn{2}{c|}{$\\overline{\mbox{pos. by chunks}}$} ' +
              '\\\\ \\hline')
        rows = all_stats['lines']['by_mean']
        for i, mkey in enumerate(rows):
            skey, _, num = mkey.rpartition('_')
            mname = HUMAN_NAMES[skey].replace('{num}', num)
            print('%s & %d. & %.2f & %d. & %.2f \\\\' % (
                mname.replace('_', '\\_'),
                i + 1,
                all_stats['lines']['means'][mkey],
                all_stats['len']['by_mean'].index(mkey) + 1,
                all_stats['len']['means'][mkey]))
        print('\\end{tabular}')
        sys.stderr.write('printed %r rows\n' % len(rows))
    else:
        for k, stats in sorted(all_stats.items()):
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
    parser.add_argument('--latex', action='store_true', help='Output LaTeX')
    parser.add_argument('-i', '--input-file', metavar='FILE', help='Read results from this file instead of the default')
    parser.add_argument('--days', metavar='DAYS', help='Diff days', type=int, default=60)
    args = parser.parse_args()

    if args.input_file:
        experiments = utils.read_json(args.input_file)
    else:
        experiments = utils.read_data('experiments', dirname=sim.DIRNAME)
    print_results(args, experiments)


if __name__ == '__main__':
    main()