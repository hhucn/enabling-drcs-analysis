#!/usr/bin/env python3

import argparse
import statistics

import sim
import utils


def eval_results(experiments):
    for i, e in enumerate(experiments):
        print('[%d] %s (%d heads), %s -> %s' % (
            i, e['repo'], len(e['all_heads']), utils.datestr(e['ts']), utils.datestr(e['future_ts'])))
        for k, results in sorted(e['res'].items()):
            results = sorted(results, key=lambda r: r['diff']['lines'])
            result_vals = [r['diff']['lines'] for r in results]
            best = results[0]
            second_str = (
                '(%2d) %6d' % (results[1]['param'], results[1]['diff']['lines'])
                if len(results) > 1
                else '%11s' % '-')

            print(' %-24s: best(%2d) %6d   2best%s   avg %6d   median %6d   max %6d   first %6d   last %6d' % (
                '%s[%d]' % (k, len(results)),
                best['param'], best['diff']['lines'],
                second_str,
                statistics.mean(result_vals), statistics.median(result_vals),
                max(result_vals),
                result_vals[0], result_vals[-1],
                ))


def main():
    parser = argparse.ArgumentParser(
        'Compare and display simulation results')
    parser.parse_args()

    experiments = utils.read_data('experiments', dirname=sim.DIRNAME)
    eval_results(experiments)


if __name__ == '__main__':
    main()
