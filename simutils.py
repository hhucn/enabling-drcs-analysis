import git

import diff
import graph


def merge_greedy(tmp_repo, shas):
    tmp_repo.git.checkout(shas[0], force=True)
    merged = [shas[0]]
    for sha in shas[1:]:
        try:
            tmp_repo.git.merge(sha)
        except git.exc.GitCommandError:
            tmp_repo.git.execute(['git', 'reset', '--hard', tmp_repo.head.object.hexsha])
            continue
        merged.append(sha)
    return merged


def get_metadata(commit_dict, sha):
    cinfo = commit_dict[sha]
    return {
        'size': graph.calc_size(commit_dict, cinfo),
        'depth': cinfo['depth'],
        'sha': cinfo['sha'],
    }


def merge_greedy_diff_all(tmp_repo, commit_dict, future_commit, shas, head_counts):
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

        try:
            tmp_repo.git.merge(sha)
        except git.exc.GitCommandError:
            tmp_repo.git.execute(['git', 'reset', '--hard', tmp_repo.head.object.hexsha])
            continue
        merged.append(sha)

    return all_res


def eval_all_straight(tmp_repo, commit_dict, future_commit, shas):
    all_res = []
    for i, sha in enumerate(shas):
        commit = tmp_repo.commit(sha)
        res = get_metadata(commit_dict, sha)
        res['diff'] = diff.eval(future_commit, commit)
        res['param'] = res['index'] = i
        all_res.append(res)
    return all_res
