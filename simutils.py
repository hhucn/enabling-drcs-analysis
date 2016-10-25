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
    cur_sha = tmp_repo.head.object.hexsha
    try:
        tmp_repo.git.merge(sha)
        return True
    except git.exc.GitCommandError:
        unmerged_blobs = tmp_repo.index.unmerged_blobs()
        fns = list(unmerged_blobs)
        give_up = False
        try:
            tmp_repo.git.execute(['git', 'checkout', cur_sha, '--'] + fns)
        except git.exc.GitCommandError:
            # TODO better: complicated, give up
            give_up = True

        if give_up or list(tmp_repo.index.unmerged_blobs()):
            try:
                tmp_repo.git.execute(['git', 'commit', '-am', 'accept anything open'])
                return True
            except git.exc.GitCommandError:
                pass

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
