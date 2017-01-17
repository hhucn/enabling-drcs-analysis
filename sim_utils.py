import random

import checksum
import diff
import gen_commit_lists
import graph
import merge
import utils

import git


RESULTS_DIRNAME = 'sim_results'


class SimulationError(BaseException):
    def __init__(self, message):
        super().__init__(message)
        self.message = message


def get_metadata(commit_dict, sha):
    cinfo = commit_dict[sha]
    return {
        'size': graph.calc_size(commit_dict, cinfo),
        'depth': cinfo['depth'],
        'sha': cinfo['sha'],
    }


def merge_greedy_diff_all(tmp_repo, future_commits, shas, head_counts, mergefunc=merge.merge_once):
    assert head_counts == sorted(head_counts)
    hc_it = iter(head_counts)
    hc = next(hc_it)
    all_res = []
    try:
        tmp_repo.git.checkout(shas[0], force=True)
    except git.exc.GitCommandError as gce:
        raise SimulationError(gce.stderr)

    merged = [shas[0]]
    for idx, sha in enumerate(shas[1:], start=1):
        assert idx <= hc
        if idx == hc:
            res = {}
            res['head_count'] = hc
            res['param'] = hc
            res['merged_commits'] = merged[:]
            res['diffs'] = diff.eval_all(future_commits, None)
            all_res.append(res)

            try:
                hc = next(hc_it)
            except StopIteration:
                break

        if mergefunc(tmp_repo, sha):
            merged.append(sha)

    return all_res


def merge_ours_greedy_diff_all(tmp_repo, future_commits, shas, head_counts):
    return merge_greedy_diff_all(tmp_repo, future_commits, shas, head_counts, mergefunc=merge.merge_ours)


def eval_all_straight(tmp_repo, commit_dict, future_commits, shas):
    all_res = []
    for i, sha in enumerate(shas):
        commit = tmp_repo.commit(sha)
        res = get_metadata(commit_dict, sha)
        res['diffs'] = diff.eval_all(future_commits, commit)
        res['param'] = res['index'] = i
        all_res.append(res)
    return all_res


def check_experiment(params, warn_func):
    repo_dict = params['repo_dict']
    config = params['config']
    seed = params['seed']

    rng = random.Random(seed)
    basename = utils.safe_filename(repo_dict['full_name'])

    if not utils.data_exists(basename, gen_commit_lists.DIRNAME):
        warn_func('%s: No commit list, skipping.' % repo_dict['full_name'])
        return False

    sim_config = config['sim']

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
        warn_func('%s: No experiment possible: Time range to small. Ignoring ...' % repo_dict['full_name'])
        return False

    ts = rng.randint(first_time, last_time)
    heads = list(graph.find_all_heads(commit_dict, ts))
    if len(heads) < sim_config['min_heads']:
        warn_func('%s: Ignoring because only %d heads (<%d)' % (basename, len(heads), sim_config['min_heads']))
        return False

    def find_master_commit(ts):
        c = commit_dict[commit_list_data['master_head']]
        while c['ts'] > ts:
            parents = c['parents']
            if not parents:
                return None
            c = commit_dict[parents[0]]
        return c

    if not find_master_commit(ts):
        warn_func('%s: Cannot find master at time %s' % (basename, utils.timestr(ts)))
        return False

    return True


def calc_fn(params):
    return utils.safe_filename(
        '%05d_%s_%s' % (
            params['idx'],
            params['repo_dict']['full_name'],
            checksum.dict_checksum(params))
    )


def read_results():
    tasks = utils.read_data('sim_tasks')
    res = []
    for params in tasks:
        fn = calc_fn(params)
        if utils.data_exists(fn, dirname=RESULTS_DIRNAME):
            r = utils.read_data(fn, dirname=RESULTS_DIRNAME)
            if not r.get('errored'):
                res.append(r)
    return res
