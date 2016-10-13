import git

import diff
import graph


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
        tmp_repo.git.execute(['git', 'reset', '--hard', tmp_repo.head.object.hexsha])
        return False


def merge_ours(tmp_repo, sha):
    try:
        tmp_repo.git.merge(sha, 'ours')
        return True
    except git.exc.GitCommandError:
        tmp_repo.git.execute(['git', 'reset', '--hard', tmp_repo.head.object.hexsha])
        return False


def accept_once(tmp_repo, sha):
    try:
        tmp_repo.git.merge(sha)
        return True
    except git.exc.GitCommandError:
        fns = list(tmp_repo.index.unmerged_blobs())
        prev_blobs = list(tmp_repo.index.iter_blobs())
        print('CHECKING OUT')
        tmp_repo.git.execute(['git', 'checkout', '--ours', '--'] + fns)
        remaining_blobs = list(tmp_repo.index.iter_blobs())
        print(tmp_repo.git.execute(['git', 'status']))
        print(tmp_repo.working_dir)
        import time
        time.sleep(10000)
        print('remaingin_blobs: %r' % remaining_blobs)
        assert len(prev_blobs) > len(remaining_blobs)
        tmp_repo.git.execute(['git', 'commit', '-am', 'accept anything open'])

        tmp_repo.git.execute(['git', 'reset', '--hard', tmp_repo.head.object.hexsha])
        return False


# Testing only atm
def merge_greedy(tmp_repo, shas):
    tmp_repo.git.checkout(shas[0], force=True)
    merged = [shas[0]]
    for sha in shas[1:]:
        if merge_once(tmp_repo, sha):
            merged.append(sha)
    return merged


def merge_greedy_diff_all(tmp_repo, future_commit, shas, head_counts, mergefunc=merge_once):
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
            res['diff'] = diff.eval(future_commit, None)
            all_res.append(res)

            try:
                hc = next(hc_it)
            except StopIteration:
                break

        if mergefunc(tmp_repo, sha):
            merged.append(sha)

    return all_res


def accept_greedy_diff_all(tmp_repo, future_commit, shas, head_counts):
    return merge_greedy_diff_all(tmp_repo, future_commit, shas, head_counts, mergefunc=accept_once)


def merge_ours_greedy_diff_all(tmp_repo, future_commit, shas, head_counts):
    return merge_greedy_diff_all(tmp_repo, future_commit, shas, head_counts, mergefunc=merge_ours)


def eval_all_straight(tmp_repo, commit_dict, future_commit, shas):
    all_res = []
    for i, sha in enumerate(shas):
        commit = tmp_repo.commit(sha)
        res = get_metadata(commit_dict, sha)
        res['diff'] = diff.eval(future_commit, commit)
        res['param'] = res['index'] = i
        all_res.append(res)
    return all_res
