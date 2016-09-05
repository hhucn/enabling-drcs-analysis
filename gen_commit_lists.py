#!/usr/bin/env python3

import argparse
import collections

import git

import download
import utils
import download_prs


DIRNAME = 'commit_list'


def gen_commit_list(args, repo_dict):
    basename = utils.safe_filename(repo_dict['full_name'])

    if not utils.data_exists(basename, download_prs.DIRNAME):
        if args.verbose or args.no_status:
            print('Not all PRs downloaded for %s' % repo_dict['full_name'])
        return

    path = utils.calc_filename(basename, dirname=download.DIRNAME, suffix='')
    repo = git.repo.Repo(path)

    if args.verbose:
        print('Extracting commit list from %s' % (repo_dict['full_name']))

    def _collect_commit(c):
        return {
            'parents': tuple(p.hexsha for p in c.parents),
            'sha': c.hexsha,
            'ts': c.committed_date,
        }

    commits = {c.hexsha: _collect_commit(c) for c in repo.iter_commits()}
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
            branch_commits[c.hexsha] = _collect_commit(c)
            to_visit.extend(c.parents)

        if any_common:
            commits.update(branch_commits)
        else:
            print('No common commits for %s : %s (%d commits)' % (
                repo_dict['full_name'], b.name, len(branch_commits)))
            separate_branches.add(b.name)

    commit_list = sorted(
        commits.values(),
        key=lambda cd: (cd['ts'], cd['sha']))
    master_head = repo.head.commit.hexsha
    data = {
        'commit_list': commit_list,
        'separate_branches': sorted(separate_branches),
        'master_head': master_head,
    }
    utils.write_data(basename, dirname=DIRNAME, data=data)


def main():
    parser = argparse.ArgumentParser(
        'Generate a list of all commits in a repository')
    utils.iter_repos(parser, DIRNAME, gen_commit_list)

if __name__ == '__main__':
    main()
