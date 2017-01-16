import os
import random

import git

import checksum
import diff
import gen_commit_lists
import graph
import utils


RESULTS_DIRNAME = 'sim_results'


def get_metadata(commit_dict, sha):
    cinfo = commit_dict[sha]
    return {
        'size': graph.calc_size(commit_dict, cinfo),
        'depth': cinfo['depth'],
        'sha': cinfo['sha'],
    }


# Returns true if merge succesful
def merge_once(tmp_repo, sha):
    try:
        tmp_repo.git.merge(sha)
        return True
    except git.exc.GitCommandError:
        rm_gitcrap(tmp_repo.working_tree_dir)
        tmp_repo.git.execute(['git', 'reset', '--hard', tmp_repo.head.object.hexsha])
        return False


def merge_ours(tmp_repo, sha):
    cur_sha = tmp_repo.head.object.hexsha
    try:
        tmp_repo.git.merge(sha)
        return True
    except git.exc.GitCommandError:
        unmerged_blobs = tmp_repo.index.unmerged_blobs()
        fns = list(unmerged_blobs)
        give_up = False
        try:
            rm_gitcrap(tmp_repo.working_tree_dir)
            tmp_repo.git.execute(['git', 'checkout', cur_sha, '--'] + fns)
        except git.exc.GitCommandError:
            give_up = True

        if give_up or list(tmp_repo.index.unmerged_blobs()):
            try:
                tmp_repo.git.execute(['git', 'commit', '-am', 'accept anything open'])
                return True
            except git.exc.GitCommandError:
                pass

        rm_gitcrap(tmp_repo.working_tree_dir)
        tmp_repo.git.execute(['git', 'reset', '--hard', cur_sha])
        return False


# Testing only atm
def merge_greedy(tmp_repo, shas):
    tmp_repo.git.checkout(shas[0], force=True)
    merged = [shas[0]]
    for sha in shas[1:]:
        if merge_once(tmp_repo, sha):
            merged.append(sha)
    return merged


def merge_greedy_diff_all(tmp_repo, future_commits, shas, head_counts, mergefunc=merge_once):
    assert head_counts == sorted(head_counts)
    hc_it = iter(head_counts)
    hc = next(hc_it)
    all_res = []
    tmp_repo.git.checkout(shas[0], force=True)
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
    return merge_greedy_diff_all(tmp_repo, future_commits, shas, head_counts, mergefunc=merge_ours)


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
            res.append(r)
    return res


def rm_gitcrap(basepath):
    for dirpath, dirnames, filenames in os.walk(basepath, topdown=True):
        if '.git' in dirnames:
            dirnames.remove('.git')
        if '.gitmodules' in filenames:
            os.unlink(os.path.join(dirpath, '.gitmodules'))
