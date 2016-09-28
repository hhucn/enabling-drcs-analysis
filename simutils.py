import collections

import git

import diff
import graph

def merge_greedy(tmp_repo, shas):
    tmp_repo.git.checkout(shas[0], force=True)
    merged = [shas[0]]
    assert tmp_repo.head.object.hexsha == merged[0]
    for sha in shas[1:]:
        try:
            tmp_repo.git.merge(sha)
        except git.exc.GitCommandError as gce:
            tmp_repo.git.execute(['git', 'reset', '--hard', tmp_repo.head.object.hexsha])
            continue
        merged.append(sha)
    return merged


def merge_greedy_diff(tmp_repo, shas, future_commit):
    merged = merge_greedy(tmp_repo, shas)
    diffe = diff.eval(future_commit, None)
    diffe['merged_commits'] = merged
    return diffe


def eval_straight(tmp_repo, commit_dict, future_commit, sha):
    commit = tmp_repo.commit(sha)
    cinfo = commit_dict[sha]
    return {
        'diff': diff.eval(future_commit, commit),
        'size': graph.calc_size(commit_dict, cinfo),
        'depth': cinfo['depth'],
        'sha': cinfo['sha'],
    }
