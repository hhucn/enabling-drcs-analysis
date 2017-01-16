#!/usr/bin/env python3
from __future__ import division

import argparse
import statistics


import sim
import utils


def cv(data):
    return statistics.stdev(data) / statistics.mean(data)


def eval_days(args, experiments):
    futures = experiments[0]['futures']
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
    for eid, e in enumerate(experiments):
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
            for ex in by_days[d]['lines_by_experiment'].values())
        for d in days))))
    print('Median diff lines \\\\ (median strategy) & %s \\\\ \\hline' % (' & '.join('%s' % (
        statistics.median(
            statistics.median(ex.values())
            for ex in by_days[d]['lines_by_experiment'].values())
        for d in days))))
    # print('Median diff lines \\\\ (master) & %s \\\\ \\hline' % (' & '.join('%s' %
    #     statistics.median(
    #         ex['master_0']
    #         for ex in by_days[d]['lines_by_experiment'].values())
    #     for d in days)))
    print('Median diff lines \\\\ (All strategies) & %s \\\\ \\hline' % (' & '.join('%s' % (
        statistics.median(by_days[d]['all_line_diffs']) for d in days))))
    print('Median diff lines \\\\ (worst strategy) & %s \\\\ \\hline' % (' & '.join('%s' % (
        statistics.median(
            max(ex.values())
            for ex in by_days[d]['lines_by_experiment'].values())
        for d in days))))
    print('\\\\ \hline')
    print('Median diff chunks \\\\ (best strategy) & %s \\\\ \\hline' % (' & '.join('%s' % (
        statistics.median(
            min(ex.values())
            for ex in by_days[d]['chunks_by_experiment'].values())
        for d in days))))
    print('Median diff chunks \\\\ (median strategy) & %s \\\\ \\hline' % (' & '.join('%s' % (
        statistics.median(
            statistics.median(ex.values())
            for ex in by_days[d]['chunks_by_experiment'].values())
        for d in days))))
    # print('Median diff chunks \\\\ (master) & %s \\\\ \\hline' % (' & '.join('%s' %
    #     statistics.median(
    #         ex['master_0']
    #         for ex in by_days[d]['chunks_by_experiment'].values())
    #     for d in days)))
    print('Median diff chunks \\\\ (All strategies) & %s \\\\ \\hline' % (' & '.join('%s' % (
        statistics.median(by_days[d]['all_chunk_diffs']) for d in days))))
    print('Median diff chunks \\\\ (worst strategy) & %s \\\\ \\hline' % (' & '.join('%s' % (
        statistics.median(
            max(ex.values())
            for ex in by_days[d]['chunks_by_experiment'].values())
        for d in days))))

    # print('5\\%% quantil of CV & %s \\\\ \\hline' % (' & '.join('%d' %
    #     utils.percentile(0.5,
    #         [cv(experiment.values())
    #          for experiment in by_days[d]['lines_by_experiment'].values()]
    #     ) for d in days)))
    print('\\end{tabular}')


def main():
    parser = argparse.ArgumentParser(
        'Gather statistics about impact of the "days in the future" parameter')
    parser.add_argument('-i', '--input-file', metavar='FILE', help='Read results from this file instead of the default')
    args = parser.parse_args()

    if args.input_file:
        experiments = utils.read_json(args.input_file)
    else:
        experiments = utils.read_data('experiments', dirname=sim.DIRNAME)

    eval_days(args, experiments)


if __name__ == '__main__':
    main()
