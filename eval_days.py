#!/usr/bin/env python3
from __future__ import division

import argparse
import statistics


import sim_utils


def cv(data):
    return statistics.stdev(data) / statistics.mean(data)


def eval_days(args, results):
    futures = results[0]['futures']
    by_days = {
        f['days']: {
            'total_num_results': 0,  # Number of total results evaluated
            'all_line_diffs': [],
            'all_chunk_diffs': [],
            'all_files_diffs': [],
            'lines_by_experiment': {},
            'chunks_by_experiment': {},
        } for f in futures
    }
    for eid, e in enumerate(results):
        for family, results in e['res'].items():
            for result in results:
                strat_id = '%s_%s' % (family, result['param'])
                for diff, future in zip(result['diffs'], e['futures']):
                    day_res = by_days[future['days']]

                    day_res['total_num_results'] += 1
                    day_res['all_line_diffs'].append(diff['lines'])
                    day_res['all_chunk_diffs'].append(diff['len'])
                    day_res['all_files_diffs'].append(diff['files'])

                    lines_by_experiment = day_res['lines_by_experiment'].setdefault(eid, {})
                    assert strat_id not in lines_by_experiment
                    lines_by_experiment[strat_id] = diff['lines']

                    chunks_by_experiment = day_res['chunks_by_experiment'].setdefault(eid, {})
                    assert strat_id not in chunks_by_experiment
                    chunks_by_experiment[strat_id] = diff['len']

    days = sorted(by_days.keys())

    print('\\begin{tabular}[here]{l|%s}' % ''.join('r' for _ in days))
    print('Days & %s \\\\ \\hline' % (' & '.join('%s' % d for d in days)))
    print('\\\\ \hline')
    print('Median diff lines \\\\ (best strategy) & %s \\\\ \\hline' % (' & '.join('%s' % (
        statistics.median(
            min(ex.values())
            for ex in by_days[d]['lines_by_experiment'].values()
        ))
        for d in days)))
    print('Median diff lines \\\\ (median strategy) & %s \\\\ \\hline' % (' & '.join('%s' % (
        statistics.median(
            statistics.median(ex.values())
            for ex in by_days[d]['lines_by_experiment'].values()
        ))
        for d in days)))
    print('Median diff lines \\\\ (worst strategy) & %s \\\\ \\hline' % (' & '.join('%s' % (
        statistics.median(
            max(ex.values())
            for ex in by_days[d]['lines_by_experiment'].values()
        ))
        for d in days)))

    print('\\\\ \hline')
    print('Median diff chunks \\\\ (best strategy) & %s \\\\ \\hline' % (' & '.join('%s' % (
        statistics.median(
            min(ex.values())
            for ex in by_days[d]['chunks_by_experiment'].values()
        ))
        for d in days)))
    print('Median diff chunks \\\\ (median strategy) & %s \\\\ \\hline' % (' & '.join('%s' % (
        statistics.median(
            statistics.median(ex.values())
            for ex in by_days[d]['chunks_by_experiment'].values()
        ))
        for d in days)))
    print('Median diff chunks \\\\ (worst strategy) & %s \\\\ \\hline' % (' & '.join('%s' % (
        statistics.median(
            max(ex.values())
            for ex in by_days[d]['chunks_by_experiment'].values()
        ))
        for d in days)))
    print('\\end{tabular}')


def main():
    parser = argparse.ArgumentParser(
        'Gather statistics about impact of the "days in the future" parameter')
    args = parser.parse_args()

    results = sim_utils.read_results()
    eval_days(args, results)


if __name__ == '__main__':
    main()
