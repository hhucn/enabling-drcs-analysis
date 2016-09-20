#!/usr/bin/env python3

import argparse
import collections
import random
import time

import shutil

import git

import download
import graph
import utils
import gen_commit_lists


DIRNAME = 'sim_results'
TMP_REPOS = 'sim_tmp'


def eval_diff(diff):
    #print(diff[0].b_blob.size)
    blob_size = sum(d.b_blob.size if d.b_blob else 0 for d in diff)

    # TODO evaluate more here
    return {
        'len': len(diff),
        'blob_size': blob_size,
    }


# find all newest commits older than ts (but not their parents)
def find_all_heads(commit_dict, ts):
    visited = set()
    heads = set()
    to_explore = collections.deque()
    for c in commit_dict.values():
        if c['ts'] > ts:
            continue
        if c['sha'] in visited:
            continue
        visited.add(c['sha'])
        heads.add(c['sha'])
        to_explore.extend(c['parents'])
        while to_explore:
            sha = to_explore.popleft()
            if sha in heads:
                heads.remove(sha)
            if sha in visited:
                continue
            visited.add(sha)
            to_explore.extend(commit_dict[sha]['parents'])
    return heads


def pick(args, basename, repo):
    sim_config = args.config['sim']
    utils.ensure_datadir(TMP_REPOS)

    commit_list_data = utils.read_data(basename, gen_commit_lists.DIRNAME)
    commit_list = commit_list_data['commit_list']
    commit_dict = {c['sha']: c for c in commit_list}
    graph.calc_children(commit_dict)
    graph.calc_depths(commit_dict)
    graph.calc_sizes(commit_dict)

    def find_master_commit(ts):
        c = commit_dict[commit_list_data['master_head']]
        while c['ts'] > ts:
            c = commit_dict[c['parents'][0]]
        return c

    # Determine sensible times
    first_idx = round(sim_config['cutoff_commits_first'] * len(commit_list))
    first_time = commit_list[first_idx]['ts']
    last_idx = round(sim_config['cutoff_commits_last'] * len(commit_list))
    last_time = commit_list[last_idx]['ts']

    rng = random.Random(0)
    now = time.time()
    experiments = []
    for i in range(sim_config['experiments_per_repo']):
        ts = rng.randint(first_time, last_time)

        master_sha = find_master_commit(ts)['sha']

        future_ts = (
            ts + 24 * 60 * 60 * sim_config['master_comparison_future_days'])
        future_sha = find_master_commit(future_ts)['sha']

        heads = find_all_heads(commit_dict, ts)
        sorted_heads = sorted(
            heads,
            key=lambda sha: commit_dict[sha]['ts'],
            reverse=True)
        newest_heads = sorted_heads[:9]

        suffix = '-' + utils.timestr(now) + ('-%d' % i)
        tmp_repo_path = utils.calc_filename(
            basename, dirname=TMP_REPOS, suffix=suffix)
        assert basename in tmp_repo_path

        res = {}
        try:
            repo.clone(tmp_repo_path)
            tmp_repo = git.repo.Repo(tmp_repo_path)

            master_commit = tmp_repo.commit(master_sha)
            future_commit = tmp_repo.commit(future_sha)

            res['master'] = eval_diff(future_commit.diff(master_commit))

            for i, h in enumerate(newest_heads):
                head_commit = tmp_repo.commit(h)
                diffr = eval_diff(future_commit.diff(head_commit))
                cinfo = commit_dict[h]
                diffr['size'] = cinfo['size']
                diffr['depth'] = cinfo['depth']
                res['head_%d_%s' % (i, h)] = diffr


                tmp_repo.git.checkout(master_commit, force=True)
                #tmp_repo.merge(head_commit)
                #res['merged_%d_%s' % (i, h)] = eval_diff(future_commit.diff())
            # TODO find one or more challengers and calculate their diffs

        finally:
            if not args.keep:
                shutil.rmtree(tmp_repo_path)

        experiment = {
            'i': i,
            'ts': ts,
            'master_sha': master_sha,
            'future_ts': future_ts,
            'future_sha': future_sha,
            'res': res,
        }
        utils.evince(experiment)
        experiments.append(experiment)

    utils.write_data(basename, dirname=DIRNAME, data={
        'config': sim_config,
        'experiments': experiments,
    })


def sim_pick(args, repo_dict):
    basename = utils.safe_filename(repo_dict['full_name'])

    if not utils.data_exists(basename, gen_commit_lists.DIRNAME):
        if args.verbose or args.no_status:
            print('No commit list for %s' % repo_dict['full_name'])
        return

    path = utils.calc_filename(basename, dirname=download.DIRNAME, suffix='')
    repo = git.repo.Repo(path)

    pick(args, basename, repo)


def main():
    parser = argparse.ArgumentParser(
        'Pick random times and commits for experiments')
    parser.add_argument(
        '-k', '--keep', action='store_true',
        help='Keep temporary repositories'
    )
    utils.iter_repos(parser, DIRNAME, sim_pick)

if __name__ == '__main__':
    main()
