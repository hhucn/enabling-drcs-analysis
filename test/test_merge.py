import os.path
import subprocess
import sys
import tempfile
import unittest

import git

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


class MergeTest(unittest.TestCase):
    def test_merge_greedy_working(self):
        import simutils

        with tempfile.TemporaryDirectory(suffix='df-gha-test') as td:
            def _cmd(argv, **kwargs):
                subprocess.check_call(argv, cwd=td, stdout=subprocess.DEVNULL, **kwargs)

            _cmd(['git', 'init'])
            tmp_repo = git.Repo(td)

            fn = os.path.join(td, 'txtfile')
            new_fn = os.path.join(td, 'newfn')
            with open(fn, 'w') as f:
                f.write('The quick\ngreen\nrabbit\njumped\n')
            _cmd(['git', 'add', fn])
            _cmd(['git', 'commit', '-m', 'v1'])
            _cmd(['git', 'tag', 'v1'])
            with open(fn, 'w') as f:
                f.write('The quick\ngreen\nrabbit\njumped\nover a fence\n')
            _cmd(['git', 'commit', '-am', 'v2'])
            _cmd(['git', 'tag', 'v2'])
            _cmd(['git', 'checkout', '-b', 'alt', 'v1'], stderr=subprocess.DEVNULL)
            with open(fn, 'w') as f:
                f.write('The quick\nbrown\nrabbit\njumped\n')
            _cmd(['git', 'commit', '-am', 'v3'])
            _cmd(['git', 'tag', 'v3'])

            simutils.merge_greedy(tmp_repo, ['v2', 'v3'])
            with open(fn, 'r') as f:
                content = f.read()
            self.assertEqual(content, 'The quick\nbrown\nrabbit\njumped\nover a fence\n')

            _cmd(['git', 'checkout', '-b', 'broken', 'v1'], stderr=subprocess.DEVNULL)
            with open(fn, 'w') as f:
                f.write('The quick\nblue\nrabbit\njumped\n')
            _cmd(['git', 'commit', '-am', 'v4'])
            _cmd(['git', 'tag', 'v4'])
            merged = simutils.merge_greedy(tmp_repo, ['v3', 'v4'])
            self.assertEqual(merged, ['v3'])
            with open(fn, 'r') as f:
                content = f.read()
            self.assertEqual(content, 'The quick\nbrown\nrabbit\njumped\n')

            merged = simutils.merge_greedy(tmp_repo, ['v4', 'v3'])
            self.assertEqual(merged, ['v4'])
            with open(fn, 'r') as f:
                content = f.read()
            self.assertEqual(content, 'The quick\nblue\nrabbit\njumped\n')

if __name__ == '__main__':
    unittest.main()
