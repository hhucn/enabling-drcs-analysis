#!/usr/bin/env python3

import argparse
import functools
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
import git_utils
import graph
import sim_utils
import utils


TMP_REPOS = 'tmp_repos'


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


def run(arg_dict, params):
    repo_dict = params['repo_dict']
    config = params['config']
    seed = params['seed']
    is_parallel = arg_dict['parallel']

    fn = sim_utils.calc_fn(params)

    # Already did this experiment?
    if utils.data_exists(fn, dirname=sim_utils.RESULTS_DIRNAME) and not arg_dict['redo']:
        msg = '[%d/%d] %s (seed: %d): done already, reading result' % (
            params['idx'], params['n'], repo_dict['full_name'], seed)
        print_log(is_parallel, msg)
        return utils.read_data(fn, dirname=sim_utils.RESULTS_DIRNAME)

    msg = '[%d/%d] %s (seed: %d)' % (params['idx'], params['n'], repo_dict['full_name'], seed)
    print_log(is_parallel, msg)

    rng = random.Random(seed)
    basename = utils.safe_filename(repo_dict['full_name'])

    if not utils.data_exists(basename, gen_commit_lists.DIRNAME):
        raise Exception('No commit list for %s, skipping.' % repo_dict['full_name'])

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
    future_days = sim_config['master_comparison_future_days']
    future_durations = [24 * 60 * 60 * fd for fd in future_days]
    last_time = max_time - max(future_durations)

    if last_time < first_time:
        raise Exception('No experiment possible: Time range to small. Ignoring ...')

    ts = rng.randint(first_time, last_time)
    heads = sorted(graph.find_all_heads(commit_dict, ts))
    if len(heads) < sim_config['min_heads']:
        raise Exception('Ignoring %s: only %d heads (<%d)' % (basename, len(heads), sim_config['min_heads']))

    graph.calc_children(commit_dict)
    graph.calc_depths(commit_dict)

    def find_master_commit(ts):
        c = commit_dict[commit_list_data['master_head']]
        while c['ts'] > ts:
            c = commit_dict[c['parents'][0]]
        return c

    master_sha = find_master_commit(ts)['sha']

    futures = []
    for fd in future_days:
        fd_duration_secs = 24 * 60 * 60 * fd
        fd_ts = ts + fd_duration_secs
        futures.append({
            'days': fd,
            'duration': fd_duration_secs,
            'ts': fd_ts,
            'sha': find_master_commit(fd_ts)['sha'],
        })

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

    suffix = '-%s-%d-%d' % (utils.timestr(time.time()), seed, os.getpid())
    tmp_repo_path = utils.calc_filename(
        basename, dirname=TMP_REPOS, suffix=suffix)
    assert basename in tmp_repo_path

    experiment = {
        'repo': basename,
        'all_heads': by_crits['depth'],
        'ts': ts,
        'master_sha': master_sha,
        'futures': futures,
        'config': sim_config,
        'params': params,
    }

    res = {}
    try:
        repo.clone(tmp_repo_path)
        tmp_repo = git.repo.Repo(tmp_repo_path)

        future_commits = [tmp_repo.commit(f['sha']) for f in futures]

        res['master'] = sim_utils.eval_all_straight(tmp_repo, commit_dict, future_commits, [master_sha])

        for ckey, shas in sorted(by_crits.items()):
            res['merge_greedy_%s' % ckey] = (
                sim_utils.merge_greedy_diff_all(tmp_repo, future_commits, shas, head_counts))
            res['mours_greedy_%s' % ckey] = (
                sim_utils.merge_ours_greedy_diff_all(tmp_repo, future_commits, shas, head_counts))
            res['topmost_%s' % ckey] = (
                sim_utils.eval_all_straight(tmp_repo, commit_dict, future_commits, shas[:max_head_count])
            )

        if not arg_dict['keep']:
            shutil.rmtree(tmp_repo_path)
    except KeyboardInterrupt:
        if not arg_dict['keep']:
            shutil.rmtree(tmp_repo_path)
        raise
    except sim_utils.SimulationError as se:
        if not arg_dict['keep']:
            shutil.rmtree(tmp_repo_path)
        experiment['errored'] = True
        experiment['error_message'] = se.message
    except Exception as e:
        raise
    else:
        experiment['res'] = res

    utils.write_data(fn, experiment, dirname=sim_utils.RESULTS_DIRNAME)
    return experiment


def run_experiments(args):
    tasks = utils.read_data('sim_tasks')
    if args.start_at:
        tasks = tasks[args.start_at:]
    arg_dict = {
        'parallel': args.parallel,
        'keep': args.keep,
        'redo': args.redo,
    }
    run_with_args = functools.partial(run, arg_dict)

    make_pool = multiprocessing.Pool if args.parallel else utils.EmptyContextManager

    with make_pool() as pool:
        map_func = pool.imap_unordered if args.parallel else map
        try:
            for _ in map_func(run_with_args, tasks):
                pass
        except KeyboardInterrupt:
            traceback.print_exc()


def main():
    parser = argparse.ArgumentParser(
        'Run experiments at random times')
    parser.add_argument(
        '-p', '--parallel', action='store_true',
        help='Run in parallel'
    )
    parser.add_argument(
        '-k', '--keep',
        action='store_true',
        help='Keep temporary directories')
    parser.add_argument(
        '-r', '--redo',
        default=False,
        action='store_true',
        help='Do experiments that have been done already')
    parser.add_argument(
        '-s', '--start-at', metavar='INDEX',
        default=0,
        type=int,
        help='Start at the specified index (i.e. skip the first INDEX experiments)')
    args = parser.parse_args()

    config = utils.read_config()
    utils.ensure_datadir(TMP_REPOS)
    utils.ensure_datadir(sim_utils.RESULTS_DIRNAME)
    args.config = config

    git_utils.setup()

    run_experiments(args)


if __name__ == '__main__':
    main()
