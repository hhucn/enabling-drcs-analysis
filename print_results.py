#!/usr/bin/env python3

import argparse
import re
import statistics

import sim
import utils


def eval_results(args, experiments):
    for i, e in enumerate(experiments):
        if args.filter and not re.search(args.filter, e['repo']):
            continue

        idx = next(
            i for i, f in enumerate(e['futures'])
            if f['days'] == args.days)

        print('[%d] %s (%d heads), %s -> %s' % (
            i, e['repo'], len(e['all_heads']), utils.datestr(e['ts']), utils.datestr(e['futures'][idx]['ts'])))
        for k, all_results in sorted(e['res'].items()):
            results = sorted(all_results, key=lambda r: r['diffs'][idx][args.diff_crit])
            result_vals = [r['diffs'][idx][args.diff_crit] for r in results]
            best = results[0]
            second_str = (
                '(%2d) %6d' % (results[1]['param'], results[1]['diffs'][idx][args.diff_crit])
                if len(results) > 1
                else '%11s' % '-')

            print(' %-24s: best(%2d) %6d   2best%s   avg %6d   median %6d   max %6d   first %6d   last %6d' % (
                '%s[%d]' % (k, len(results)),
                best['param'], best['diffs'][idx][args.diff_crit],
                second_str,
                statistics.mean(result_vals), statistics.median(result_vals),
                max(result_vals),
                result_vals[0], result_vals[-1],
                ))


def main():
    parser = argparse.ArgumentParser(
        'Compare and display simulation results')
    parser.add_argument(
        '-i', '--input-file', metavar='FILE',
        help='Read results from this file instead of the default')
    parser.add_argument(
        '-d', '--diff-crit', metavar='CRIT', default='lines',
        help='Difference criterion (lines, files, or len)')
    parser.add_argument(
        '-f', '--filter', metavar='REGEXP',
        help='Filter by repo name (regular expression)')
    parser.add_argument('--days', metavar='DAYS', help='Diff days', type=int, default=60)
    args = parser.parse_args()

    if args.input_file:
        experiments = utils.read_json(args.input_file)
    else:
        experiments = utils.read_data('experiments', dirname=sim.DIRNAME)
    eval_results(args, experiments)


if __name__ == '__main__':
    main()
