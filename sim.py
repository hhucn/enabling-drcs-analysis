#!/usr/bin/env python3

import argparse
import multiprocessing
import os
import random
import re
import shutil
import time
import traceback

import git

import download
import gen_commit_lists
import graph
import simutils
import utils


DIRNAME = 'sim_results'
TMP_REPOS = 'sim_tmp'


def print_log(is_parallel, msg):
    if is_parallel:
        cp = multiprocessing.current_process()
        worker_id = cp.name
        m = re.match(r'^[a-zA-Z]+-(?P<numeric>[0-9]+)$', worker_id)
        if m:
            worker_id = m.group('numeric')
        print('{%s} %s' % (worker_id, msg))
    else:
        print('%s' % msg)


def run(params):
    repo_dict = params['repo_dict']
    config = params['config']
    seed = params['seed']
    is_parallel = params['is_parallel']

    msg = '[%d/%d] %s' % (params['idx'], params['n'], repo_dict['full_name'])
    print_log(is_parallel, msg)

    start_time = time.perf_counter()

    rng = random.Random(seed)
    basename = utils.safe_filename(repo_dict['full_name'])

    if not utils.data_exists(basename, gen_commit_lists.DIRNAME):
        print_log(is_parallel, 'No commit list for %s, skipping.' % repo_dict['full_name'])
        return

    path = utils.calc_filename(basename, dirname=download.DIRNAME, suffix='')
    repo = git.repo.Repo(path)

    sim_config = config['sim']
    utils.ensure_datadir(TMP_REPOS)

    commit_list_data = utils.read_data(basename, gen_commit_lists.DIRNAME)
    commit_list = commit_list_data['commit_list']
    commit_dict = {c['sha']: c for c in commit_list}

    # Determine sensible times
    first_idx = round(sim_config['cutoff_commits_first'] * len(commit_list))
    first_time = commit_list[first_idx]['ts']
    max_time = commit_list[-1]['ts']
    future_duration = 24 * 60 * 60 * sim_config['master_comparison_future_days']
    last_time = max_time - future_duration

    if last_time < first_time:
        print_log(is_parallel, 'No experiment possible: Time range to small. Ignoring ...')
        return

    ts = rng.randint(first_time, last_time)
    future_ts = ts + future_duration

    heads = sorted(graph.find_all_heads(commit_dict, ts))
    if len(heads) < sim_config['min_heads']:
        print_log(is_parallel, 'Ignoring %s: only %d heads (<%d)' % (basename, len(heads), sim_config['min_heads']))
        return

    graph.calc_children(commit_dict)
    graph.calc_depths(commit_dict)

    def find_master_commit(ts):
        c = commit_dict[commit_list_data['master_head']]
        while c['ts'] > ts:
            c = commit_dict[c['parents'][0]]
        return c

    master_sha = find_master_commit(ts)['sha']

    future_sha = find_master_commit(future_ts)['sha']

    author_counts = graph.count_authors(commit_dict, ts)

    def _select_random():
        random_heads = list(heads)
        rng.shuffle(random_heads)
        return random_heads

    def _select(crit_func):
        return sorted(
            heads,
            key=lambda sha: (crit_func(sha), sha),
            reverse=True)

    by_crits = {
        'ts': _select(lambda sha: commit_dict[sha]['ts']),
        'depth': _select(lambda sha: commit_dict[sha]['depth']),
        'size': _select(lambda sha: graph.calc_size(commit_dict, commit_dict[sha])),
        'author': _select(lambda sha: author_counts[commit_dict[sha]['author']]),
        'random': _select_random(),
    }

    head_counts = sim_config['experiments_head_counts']
    max_head_count = max(head_counts)

    suffix = '-%s-%d' % (utils.timestr(time.time()), os.getpid())
    tmp_repo_path = utils.calc_filename(
        basename, dirname=TMP_REPOS, suffix=suffix)
    assert basename in tmp_repo_path

    res = {}
    try:
        repo.clone(tmp_repo_path)
        tmp_repo = git.repo.Repo(tmp_repo_path)

        future_commit = tmp_repo.commit(future_sha)

        res['master'] = simutils.eval_all_straight(tmp_repo, commit_dict, future_commit, [master_sha])

        for ckey, shas in sorted(by_crits.items()):
            res['merge_greedy_%s' % ckey] = (
                simutils.merge_greedy_diff_all(tmp_repo, future_commit, shas, head_counts))
            res['mours_greedy_%s' % ckey] = (
                simutils.merge_ours_greedy_diff_all(tmp_repo, future_commit, shas, head_counts))
            res['topmost_%s' % ckey] = (
                simutils.eval_all_straight(tmp_repo, commit_dict, future_commit, shas[:max_head_count])
            )
    finally:
        if not config['args_keep']:
            shutil.rmtree(tmp_repo_path)

    duration = time.perf_counter() - start_time

    experiment = {
        'repo': basename,
        'all_heads': by_crits['depth'],
        'ts': ts,
        'master_sha': master_sha,
        'future_ts': future_ts,
        'future_sha': future_sha,
        'res': res,
        'config': sim_config,
        'duration': duration,
    }
    return experiment


def run_experiments(args, all_repos):
    rng = random.Random(0)
    n = args.n
    res = []

    is_parallel = args.parallel

    while len(res) < n:
        all_params = [{
            'config': args.config,
            'repo_dict': rng.choice(all_repos),
            'seed': rng.random(),
            'is_parallel': is_parallel,
            'idx': i,
            'n': n,
        } for i in range(len(res), n)]

        with multiprocessing.Pool() as pool:
            map_func = pool.imap_unordered if is_parallel else map
            try:
                new_res = map_func(run, all_params)
                for nr in new_res:
                    if nr:
                        res.append(nr)
                        print('Completed %d/%d experiments' % (len(res), n))
            except KeyboardInterrupt:
                traceback.print_exc()
                break

    return res


def main():
    parser = argparse.ArgumentParser(
        'Run experiments at random times')
    parser.add_argument(
        '-k', '--keep', action='store_true',
        help='Keep temporary repositories'
    )
    parser.add_argument(
        '-p', '--parallel', action='store_true',
        help='Run in parallel'
    )
    parser.add_argument(
        '-f', '--filter',
        metavar='REGEXP', type=re.compile,
        help='Filter by repository fullname (regular expressions)')
    parser.add_argument(
        '-n', '--experiment-count', default=100,
        metavar='COUNT', type=int, dest='n',
        help='Number of experiments to perform (default: %(default)s)')
    args = parser.parse_args()

    config = utils.read_config()
    ignored_repos = set(config.get('ignored_repos', []))

    utils.ensure_datadir(DIRNAME)
    args.config = config
    config['args_keep'] = args.keep

    def _should_visit(repo_dict):
        if repo_dict['full_name'] in ignored_repos:
            return False

        if args.filter and not args.filter.search(repo_dict['full_name']):
            return False

        return True

    all_repos = list(filter(_should_visit, utils.read_data('list')))
    experiments = []
    for e in run_experiments(args, all_repos):
        experiments.append(e)

    basename = 'experiments'
    fn = utils.calc_filename(basename, dirname=DIRNAME)
    print('Writing %d experiments to %s ...' % (len(experiments), fn))
    utils.write_data(basename, experiments, dirname=DIRNAME)


if __name__ == '__main__':
    main()
