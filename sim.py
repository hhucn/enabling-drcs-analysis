#!/usr/bin/env python3

import argparse
import collections
import random
import time

import shutil

import git

import diff
import download
import gen_commit_lists
import graph
import simutils
import utils


DIRNAME = 'sim_results'
TMP_REPOS = 'sim_tmp'


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

        sorted_time_heads = sorted(
            heads,
            key=lambda sha: commit_dict[sha]['ts'],
            reverse=True)
        sorted_depth_heads = sorted(
            heads,
            key=lambda sha: commit_dict[sha]['depth'],
            reverse=True)
        sorted_size_heads = sorted(
            heads,
            key=lambda sha: graph.calc_size(commit_dict, commit_dict[sha]))

        head_count = sim_config['experiments_head_count']
        newest_heads = sorted_time_heads[:head_count]

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

            master_info = commit_dict[master_sha]
            res['master'] = [{
                'diff': diff.eval(future_commit, master_commit),
                'size': graph.calc_size(commit_dict, master_info),
                'depth': master_info['depth'],
                'sha': master_info['sha'],
            }]

            res['newest_heads'] = []
            for i, h in enumerate(newest_heads):
                head_commit = tmp_repo.commit(h)
                cinfo = commit_dict[h]
                res['newest_heads'].append({
                    'sha': cinfo['sha'],
                    'diff': diff.eval(future_commit, head_commit),
                    'size': graph.calc_size(commit_dict, cinfo),
                    'depth': cinfo['depth'],
                })

            res['merge_greedy_newest'] = simutils.merge_greedy_diff(
                tmp_repo, newest_heads, future_commit)
            res['merge_greedy_time'] = simutils.merge_greedy_diff(
                tmp_repo, sorted_time_heads, future_commit)
            res['merge_greedy_depth'] = simutils.merge_greedy_diff(
                tmp_repo, sorted_depth_heads, future_commit)
            res['merge_greedy_size'] = simutils.merge_greedy_diff(
                tmp_repo, sorted_size_heads, future_commit)

            # TODO find one or more challengers and calculate their diffs

            # TODO order differently

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
