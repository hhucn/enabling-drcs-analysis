import git

import diff

def merge_greedy(tmp_repo, shas, future_commit):
	tmp_repo.git.checkout(shas[0], force=True)
	for sha in shas[1:]:
		print('merging %r' % sha)
		try:
			tmp_repo.git.merge(sha)
		except git.GitCommandError as gce:
			print(repr(gce))
			raise

	return diff.eval(future_commit)