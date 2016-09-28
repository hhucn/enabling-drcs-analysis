#!/usr/bin/env python3

import argparse
import os
import random
import re
import shutil
import time

import git

import download
import gen_commit_lists
import graph
import simutils
import utils


DIRNAME = 'sim_results'
TMP_REPOS = 'sim_tmp'


def run(args, basename, repo, rng):
    sim_config = args.config['sim']
    utils.ensure_datadir(TMP_REPOS)

    commit_list_data = utils.read_data(basename, gen_commit_lists.DIRNAME)
    commit_list = commit_list_data['commit_list']
    commit_dict = {c['sha']: c for c in commit_list}

    # Determine sensible times
    first_idx = round(sim_config['cutoff_commits_first'] * len(commit_list))
    first_time = commit_list[first_idx]['ts']
    last_idx = round(sim_config['cutoff_commits_last'] * len(commit_list))
    last_time = commit_list[last_idx]['ts']
    ts = rng.randint(first_time, last_time)

    heads = graph.find_all_heads(commit_dict, ts)
    if len(heads) < sim_config['min_heads']:
        print('Ignoring %s: only %d heads (<%d)' % (basename, len(heads), sim_config['min_heads']))
        return

    graph.calc_children(commit_dict)
    graph.calc_depths(commit_dict)

    def find_master_commit(ts):
        c = commit_dict[commit_list_data['master_head']]
        while c['ts'] > ts:
            c = commit_dict[c['parents'][0]]
        return c

    now = time.time()
    master_sha = find_master_commit(ts)['sha']

    future_ts = (
        ts + 24 * 60 * 60 * sim_config['master_comparison_future_days'])
    future_sha = find_master_commit(future_ts)['sha']

    author_counts = graph.count_authors(commit_dict, ts)

    def _select(crit_func):
        return sorted(
            heads,
            key=crit_func,
            reverse=True)

    by_crits = {
        'ts': _select(lambda sha: commit_dict[sha]['ts']),
        'depth': _select(lambda sha: commit_dict[sha]['depth']),
        'size': _select(lambda sha: graph.calc_size(commit_dict, commit_dict[sha])),
        'author': _select(lambda sha: author_counts[commit_dict[sha]['author']]),
    }

    head_counts = sim_config['experiments_head_counts']
    max_head_count = max(head_counts)

    suffix = '-%s-%d' % (utils.timestr(now), os.getpid())
    tmp_repo_path = utils.calc_filename(
        basename, dirname=TMP_REPOS, suffix=suffix)
    assert basename in tmp_repo_path

    res = {}
    try:
        repo.clone(tmp_repo_path)
        tmp_repo = git.repo.Repo(tmp_repo_path)

        future_commit = tmp_repo.commit(future_sha)

        res['master'] = simutils.eval_all_straight(tmp_repo, commit_dict, future_commit, [master_sha])

        for ckey, shas in by_crits.items():
            res['merge_greedy_%s' % ckey] = (
                simutils.merge_greedy_diff_all(tmp_repo, future_commit, shas, head_counts))
            res['accept_greedy_%s' % ckey] = (
                simutils.accept_greedy_diff_all(tmp_repo, future_commit, shas, head_counts))
            res['topmost_%s' % ckey] = (
                simutils.eval_all_straight(tmp_repo, commit_dict, future_commit, shas[:max_head_count])
            )
    finally:
        if not args.keep:
            shutil.rmtree(tmp_repo_path)

    experiment = {
        'repo': basename,
        'all_heads': by_crits['depth'],
        'ts': ts,
        'master_sha': master_sha,
        'future_ts': future_ts,
        'future_sha': future_sha,
        'res': res,
        'config': sim_config,
    }
    yield experiment


def run_experiments(args, all_repos):
    rng = random.Random(0)
    n = args.n
    count = 0
    while count < n:
        repo_dict = rng.choice(all_repos)

        basename = utils.safe_filename(repo_dict['full_name'])

        if not utils.data_exists(basename, gen_commit_lists.DIRNAME):
            if args.verbose or args.no_status:
                print('No commit list for %s, skipping.' % repo_dict['full_name'])
            return
        print('[%d/%d] %s' % (count, n, basename))

        path = utils.calc_filename(basename, dirname=download.DIRNAME, suffix='')
        repo = git.repo.Repo(path)

        for e in run(args, basename, repo, rng):
            count += 1
            yield e


def main():
    parser = argparse.ArgumentParser(
        'Run experiments at random times')
    parser.add_argument(
        '-k', '--keep', action='store_true',
        help='Keep temporary repositories'
    )
    parser.add_argument(
        '-f', '--filter',
        metavar='REGEXP', type=re.compile,
        help='Filter by repository fullname (regular expressions)')
    parser.add_argument(
        '-n', '--experiment-count', default=1000,
        metavar='COUNT', type=int, dest='n',
        help='Number of experiments to perform')
    args = parser.parse_args()

    config = utils.read_config()
    ignored_repos = set(config.get('ignored_repos', []))

    utils.ensure_datadir(DIRNAME)
    args.config = config

    def _should_visit(repo_dict):
        if repo_dict['full_name'] in ignored_repos:
            return False

        if args.filter and not args.filter.search(repo_dict['full_name']):
            return False

        return True

    all_repos = list(filter(_should_visit, utils.read_data('list')))
    experiments = []
    try:
        for e in run_experiments(args, all_repos):
            experiments.append(e)
    except KeyboardInterrupt:
        pass

    basename = 'experiments'
    fn = utils.calc_filename(basename, dirname=DIRNAME)
    print('Writing %d experiments to %s ...' % (len(experiments), fn))
    utils.write_data(basename, experiments, dirname=DIRNAME)


if __name__ == '__main__':
    main()
