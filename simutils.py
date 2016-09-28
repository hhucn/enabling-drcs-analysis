import git

import diff

def merge_greedy(tmp_repo, shas):
	tmp_repo.git.checkout(shas[0], force=True)
	for sha in shas[1:]:
		try:
			tmp_repo.git.merge(sha)
		except git.exc.GitCommandError as gce:
			print(tmp_repo.index.unmerged_blobs())
			#print(gce.stderr, gce.stdout)
			#print(dir(gce))
			#print(tmp_repo.git.status())
			raise Exception('foo')


def merge_greedy_diff(tmp_repos, shas, future_commit):
	merge_greedy(tmp_repo, shas)
	return diff.eval(future_commit)