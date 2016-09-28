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


def run(args, basename, repo):
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

        heads = graph.find_all_heads(commit_dict, ts)
        author_counts = graph.count_authors(commit_dict, ts)

        head_count = sim_config['experiments_head_count']
        def _select(crit_func):
            return sorted(
                heads,
                key=crit_func,
                reverse=True)[:head_count]

        by_crits = {
            'ts': _select(lambda sha: commit_dict[sha]['ts']),
            'depth': _select(lambda sha: commit_dict[sha]['depth']),
            'size': _select(lambda sha: graph.calc_size(commit_dict, commit_dict[sha])),
            'author': _select(lambda sha: author_counts[commit_dict[sha]['author']]),
        }

        suffix = '-' + utils.timestr(now) + ('-%d' % i)
        tmp_repo_path = utils.calc_filename(
            basename, dirname=TMP_REPOS, suffix=suffix)
        assert basename in tmp_repo_path

        res = {}
        try:
            repo.clone(tmp_repo_path)
            tmp_repo = git.repo.Repo(tmp_repo_path)

            future_commit = tmp_repo.commit(future_sha)

            res['master'] = simutils.eval_straight(tmp_repo, commit_dict, future_commit, master_sha)

            for ckey, shas in by_crits.items():
                res['merge_greedy_%s' % ckey] = [
                    simutils.merge_greedy_diff(tmp_repo, shas, future_commit)]
                res['topmost_%s' % ckey] = [
                    simutils.eval_straight(tmp_repo, commit_dict, future_commit, sha) for sha in shas
                ]
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


def sim_repo(args, repo_dict):
    basename = utils.safe_filename(repo_dict['full_name'])

    if not utils.data_exists(basename, gen_commit_lists.DIRNAME):
        if args.verbose or args.no_status:
            print('No commit list for %s' % repo_dict['full_name'])
        return

    path = utils.calc_filename(basename, dirname=download.DIRNAME, suffix='')
    repo = git.repo.Repo(path)

    run(args, basename, repo)


def main():
    parser = argparse.ArgumentParser(
        'Run experiments at random times')
    parser.add_argument(
        '-k', '--keep', action='store_true',
        help='Keep temporary repositories'
    )
    utils.iter_repos(parser, DIRNAME, sim_repo)

if __name__ == '__main__':
    main()
