#!/usr/bin/env python3

import argparse

import sim_utils
import utils


def main():
    parser = argparse.ArgumentParser('Print number of unique repositories in the experiments')
    parser.parse_args()

    warnings = utils.read_data('sim_warnings')
    for wcode, wrepos in warnings.items():
        print('%s: %d' % (wcode, len(wrepos)))


if __name__ == '__main__':
    main()
