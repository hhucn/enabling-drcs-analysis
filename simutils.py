import git

import diff

def merge_greedy(tmp_repo, shas):
	tmp_repo.git.checkout(shas[0], force=True)
	merged = [shas[0]]
	for sha in shas[1:]:
		try:
			tmp_repo.git.merge(sha)
		except git.exc.GitCommandError as gce:
			tmp_repo.git.execute(['git', 'merge', '--abort'])
			continue
		merged.append(sha)
	return merged


def merge_greedy_diff(tmp_repo, shas, future_commit):
	merged = merge_greedy(tmp_repo, shas)
	diffe = diff.eval(future_commit, None)
	diffe['merged_commits'] = merged
	return diffe