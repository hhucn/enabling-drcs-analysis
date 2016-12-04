#!/usr/bin/env python3
from __future__ import division

import argparse
import math
import time

import progress
import git

import download
import utils
import list_prs


DIRNAME = 'download_prs'


def download_chunks(origin, failures, prs, chunk_size):
    if chunk_size == 1:
        for pr in prs:
            try:
                origin.fetch(branch_name(pr))
            except git.exc.GitCommandError as gce:
                failures.append({
                    'pull': pr,
                    'msg': gce.stderr,
                })
    else:
        for prs_chunk in utils.chunks(prs, chunk_size):
            try:
                origin.fetch(list(map(branch_name, prs_chunk)))
            except git.exc.GitCommandError:
                new_chunk_size = max(1, int(math.floor(chunk_size / 10)))
                download_chunks(
                    origin, failures, prs_chunk, new_chunk_size)


def branch_name(pr):
    return 'pull/%d/head:gha_pr_%d' % (pr['number'], pr['number'])


def download_prs(args, repo_dict):
    basename = utils.safe_filename(repo_dict['full_name'])

    path = utils.calc_filename(basename, dirname=download.DIRNAME, suffix='')
    repo = git.repo.Repo(path)
    origin = repo.remotes.origin
    prs = utils.read_data(basename, list_prs.DIRNAME)

    if args.verbose:
        print('Fetching %d PRs from %s' % (len(prs), repo_dict['full_name']))
        prs = progress.bar.Bar(max=len(prs)).iter(prs)

    failures = []
    download_chunks(origin, failures, prs, 1000)

    utils.write_data(basename, dirname=DIRNAME, data={
        'timestamp': time.time(),
        'failures': failures,
    })

    if failures:
        print('They were %d failures for %s: %r' % (
            len(failures), basename,
            [branch_name(f['pull']) for f in failures]))


def main():
    parser = argparse.ArgumentParser('Download pull requests')
    utils.iter_repos(parser, DIRNAME, download_prs)

if __name__ == '__main__':
    main()
