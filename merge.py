import git

import git_utils


# Returns true if merge succesful
def merge_once(tmp_repo, sha):
    try:
        tmp_repo.git.merge(sha)
        return True
    except git.exc.GitCommandError:
        git_utils.check_unlocked(tmp_repo.working_tree_dir)
        git_utils.rm_gitcrap(tmp_repo.working_tree_dir)
        tmp_repo.git.execute(['git', 'reset', '--hard', tmp_repo.head.object.hexsha])
        git_utils.check_unlocked(tmp_repo.working_tree_dir)
        return False


def merge_ours(tmp_repo, sha):
    cur_sha = tmp_repo.head.object.hexsha
    try:
        tmp_repo.git.merge(sha)
        return True
    except git.exc.GitCommandError:
        git_utils.check_unlocked(tmp_repo.working_tree_dir)
        unmerged_blobs = tmp_repo.index.unmerged_blobs()
        fns = list(unmerged_blobs)
        git_utils.check_unlocked(tmp_repo.working_tree_dir)
        give_up = False
        try:
            git_utils.rm_gitcrap(tmp_repo.working_tree_dir)
            tmp_repo.git.execute(['git', 'checkout', cur_sha, '--'] + fns)
        except git.exc.GitCommandError:
            give_up = True

        git_utils.check_unlocked(tmp_repo.working_tree_dir)

        if give_up or list(tmp_repo.index.unmerged_blobs()):
            try:
                tmp_repo.git.execute(['git', 'commit', '-am', 'accept anything open'])
                return True
            except git.exc.GitCommandError:
                pass

        git_utils.check_unlocked(tmp_repo.working_tree_dir)
        git_utils.rm_gitcrap(tmp_repo.working_tree_dir)
        tmp_repo.git.execute(['git', 'reset', '--hard', cur_sha])
        git_utils.check_unlocked(tmp_repo.working_tree_dir)
        return False


# Testing only atm
def merge_greedy(tmp_repo, shas):
    tmp_repo.git.checkout(shas[0], force=True)
    merged = [shas[0]]
    for sha in shas[1:]:
        if merge_once(tmp_repo, sha):
            merged.append(sha)
    return merged
