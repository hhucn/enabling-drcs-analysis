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


def merge_greedy_diff(tmp_repo, commit_dict, future_commit, shas):
    merged = merge_greedy(tmp_repo, shas)
    res = {}
    res['merged_commits'] = merged
    res['diff'] = diff.eval(future_commit, None)
    return res


def eval_straight(tmp_repo, commit_dict, future_commit, sha):
    commit = tmp_repo.commit(sha)
    res = get_metadata(commit_dict, sha)
    res['diff'] = diff.eval(future_commit, commit)
    return res
