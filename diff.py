# See test_diff.py for some more spec

import re
import git_utils


def eval_all(future_commits, c2):
    return [eval(fc, c2) for fc in future_commits]


def eval(c1, c2):
    diffs = c1.diff(c2, create_patch=True)
    git_utils.check_unlocked(c1.repo.working_dir)

    fns = set()
    for d in diffs:
        fns.add(d.a_path)
        fns.add(d.b_path)

    lines = sum(
        len(re.findall(rb'\n[+-]', d.diff))
        for d in diffs)

    return {
        'lines': lines,
        'len': len(diffs),
        'files': len(fns),
    }
