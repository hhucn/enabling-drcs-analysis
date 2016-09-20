# See test_diff.py for some more spec

import re


def eval(c1, c2):
    diffs = c1.diff(c2, create_patch=True)

    lines = sum(
        len(re.findall(rb'\n[+-]', d.diff))
        for d in diffs)

    return {
        'lines': lines,
        'len': len(diffs),
    }
