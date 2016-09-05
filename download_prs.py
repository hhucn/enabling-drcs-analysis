#!/usr/bin/env python3

import argparse
import os.path
import time

import progress
import git

import download
import utils
import query
import list_prs



CANARY_DIRNAME = 'downloaded_prs'


def branch_name(pr):
    return 'pull/%d/head:gha_pr_%d' % (pr['number'], pr['number'])


def download_prs(repo_dict, verbose):
    basename = utils.safe_filename(repo_dict['full_name'])
    if utils.data_exists(basename, CANARY_DIRNAME):
        return

    path = utils.calc_filename(basename, dirname=download.DIRNAME, suffix='')
    repo = git.repo.Repo(path)
    origin = repo.remotes.origin
    prs = utils.read_data(basename, list_prs.DIRNAME)

    if verbose:
        print('Fetching %d PRs from %s' % (len(prs), repo_dict['full_name']))
        prs = progress.bar.Bar(max=len(prs)).iter(prs)

    failures = []
    for prs_chunk in utils.chunks(prs, 100):
        try:
            origin.fetch(list(map(branch_name, prs_chunk)))
        except git.exc.GitCommandError:
            for pr in prs_chunk:
                try:
                    origin.fetch(branch_name(pr))
                except git.exc.GitCommandError as gce:
                    failures.append({
                        'pull': pr,
                        'msg': gce.stderr.decode(),
                    })

    utils.write_data(basename, dirname=CANARY_DIRNAME, data={
        'timestamp': time.time(),
        'failures': failures,
    })

    if verbose and failures:
        print('They were %d failures for %s: %r' % (
            len(failures), basename,
            [branch_name(f['pull']) for f in failures]))


def main():
    parser = argparse.ArgumentParser('Download pull requests')
    parser.add_argument('-v', '--verbose', action='store_true', help='Show detailed status')
    args = parser.parse_args()

    utils.ensure_datadir(CANARY_DIRNAME)

    utils.iter_repos(args, 'Downloading PRs', download_prs)

if __name__ == '__main__':
    main()
