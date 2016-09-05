#!/usr/bin/env python3

import argparse
import collections
import os.path
import time

import progress
import git

import download
import utils
import query
import list_prs
import download_prs


DIRNAME = 'commit_list'


def gen_commit_list(repo_dict, verbose):
    basename = utils.safe_filename(repo_dict['full_name'])
    if utils.data_exists(basename, DIRNAME):
        return

    if not utils.data_exists(basename, download_prs.DIRNAME):
        # We haven't downloaded all PRs yet
        return

    path = utils.calc_filename(basename, dirname=download.DIRNAME, suffix='')
    repo = git.repo.Repo(path)
    origin = repo.remotes.origin
    prs = utils.read_data(basename, list_prs.DIRNAME)

    if verbose:
        print('Extracting commit list from %s' % (repo_dict['full_name']))

    commits = {c.hexsha: c.committed_date for c in repo.iter_commits()}
    separate_branches = set()
    for b in repo.branches:
        any_common = False
        branch_commits = {}
        to_visit = collections.deque([b.commit])
        while to_visit:
            c = to_visit.popleft()
            if c.hexsha in commits:
                any_common = True
                continue
            if c.hexsha in branch_commits:
                continue
            branch_commits[c.hexsha] = c.committed_date
            to_visit.extend(c.parents)

        if any_common:
            commits.update(branch_commits)
        else:
            print('No common commits for %s : %s (%d commits)' % (
                repo_dict['full_name'], b.name, len(branch_commits)))
            separate_branches.add(b.name)

    commit_items = sorted(commits.items(), key=lambda t: (t[1], t[0]))
    commit_list = [{
        'sha': sha,
        'ts': ts
    } for sha, ts in commit_items]
    data = {
        'commit_list': commit_list,
        'separate_branches': sorted(separate_branches),
    }
    utils.write_data(basename, dirname=DIRNAME, data=data)



def main():
    parser = argparse.ArgumentParser('Generate a list of all commits in a repository')
    utils.ensure_datadir(DIRNAME)
    utils.iter_repos(parser, 'Extracting commits', gen_commit_list)

if __name__ == '__main__':
    main()
