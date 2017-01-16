#!/usr/bin/env python3

import random

import gen_commit_lists
import graph
import utils


TMP_REPOS = 'sim_tmp'


def check_experiment(params, warn_func):
    repo_dict = params['repo_dict']
    config = params['config']
    seed = params['seed']

    rng = random.Random(seed)
    basename = utils.safe_filename(repo_dict['full_name'])

    if not utils.data_exists(basename, gen_commit_lists.DIRNAME):
        warn_func('No commit list for %s, skipping.' % repo_dict['full_name'])
        return False

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
        warn_func('No experiment possible: Time range to small. Ignoring ...')
        return False

    ts = rng.randint(first_time, last_time)
    heads = list(graph.find_all_heads(commit_dict, ts))
    if len(heads) < sim_config['min_heads']:
        warn_func('Ignoring %s: only %d heads (<%d)' % (basename, len(heads), sim_config['min_heads']))
        return False
