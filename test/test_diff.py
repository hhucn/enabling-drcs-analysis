import os.path
import subprocess
import sys
import tempfile
import unittest

import git

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


class DiffTest(unittest.TestCase):
    def test_diff_bin(self):
        import diff

        with tempfile.TemporaryDirectory(suffix='df-gha-test') as td:
            def _cmd(argv):
                subprocess.check_call(argv, cwd=td, stdout=subprocess.DEVNULL)

            _cmd(['git', 'init'])

            fn = os.path.join(td, 'binfile')
            with open(fn, 'wb') as f:
                f.write(b'\x00' * 100000)
            _cmd(['git', 'add', fn])
            _cmd(['git', 'commit', '-m', 'v1'])
            with open(fn, 'wb') as f:
                f.write(b'\x01' * 100000)
            _cmd(['git', 'commit', '-am', 'v2'])

            repo = git.Repo(td)

            v1 = repo.commit('master~1')
            v2 = repo.commit('master')
            dres = diff.eval(v1, v2)
            self.assertEqual(dres, {
                'len': 1,
                'lines': 0,
            })

    def test_diff_text(self):
        import diff

        with tempfile.TemporaryDirectory(suffix='df-gha-test') as td:
            def _cmd(argv):
                subprocess.check_call(argv, cwd=td, stdout=subprocess.DEVNULL)

            _cmd(['git', 'init'])

            fn = os.path.join(td, 'txtfile')
            new_fn = os.path.join(td, 'newfn')
            with open(fn, 'wb') as f:
                f.write(b'The quick\ngreen\nrabbit\njumped\n')
            _cmd(['git', 'add', fn])
            _cmd(['git', 'commit', '-m', 'v1'])
            _cmd(['git', 'tag', 'v1'])
            with open(fn, 'wb') as f:
                f.write(b'The quick\ngreen\nrabbit\njumped\nover a fence\n')
            _cmd(['git', 'commit', '-am', 'v2'])
            _cmd(['git', 'tag', 'v2'])
            with open(fn, 'wb') as f:
                f.write(b'The quick\nbrown\nrabbit\njumped\nover a fence\n')
            _cmd(['git', 'commit', '-am', 'v3'])
            _cmd(['git', 'tag', 'v3'])
            with open(fn, 'wb') as f:
                f.write(b'The quick\nbrown\nrabbit\njumped\n' +
                        b'over a fence\nand a wall\n')
            with open(new_fn, 'wb') as f:
                f.write(b'New file\nis\nnew\n')
            _cmd(['git', 'add', new_fn])
            _cmd(['git', 'commit', '-am', 'v4'])
            _cmd(['git', 'tag', 'v4'])

            repo = git.Repo(td)
            v1 = repo.commit('v1')
            v2 = repo.commit('v2')
            v3 = repo.commit('v3')
            v4 = repo.commit('v4')
            dres = diff.eval(v1, v2)
            self.assertEqual(dres, {
                'lines': 1,
                'len': 1,
            })
            dres = diff.eval(v2, v3)
            self.assertEqual(dres, {
                'lines': 2,
                'len': 1,
            })
            dres = diff.eval(v3, v4)
            self.assertEqual(dres, {
                'lines': 4,
                'len': 2,
            })

    def test_rename(self):
        import diff

        with tempfile.TemporaryDirectory(suffix='df-gha-test') as td:
            def _cmd(argv):
                subprocess.check_call(argv, cwd=td, stdout=subprocess.DEVNULL)

            _cmd(['git', 'init'])

            fn = os.path.join(td, 'txtfile')
            with open(fn, 'wb') as f:
                f.write(b'data does\nnot\nmatter\nhere\n')
            _cmd(['git', 'add', fn])
            _cmd(['git', 'commit', '-m', 'v1'])
            _cmd(['git', 'tag', 'v1'])
            _cmd(['git', 'mv', 'txtfile', 'renamed_file'])
            _cmd(['git', 'commit', '-am', 'v2'])
            _cmd(['git', 'tag', 'v2'])

            repo = git.Repo(td)
            v1 = repo.commit('v1')
            v2 = repo.commit('v2')
            dres = diff.eval(v1, v2)
            self.assertEqual(dres, {
                'lines': 0,
                'len': 1,
            })

    def test_local(self):
        import diff

        with tempfile.TemporaryDirectory(suffix='df-gha-test') as td:
            def _cmd(argv):
                subprocess.check_call(argv, cwd=td, stdout=subprocess.DEVNULL)

            _cmd(['git', 'init'])

            fn = os.path.join(td, 'txtfile')
            with open(fn, 'wb') as f:
                f.write(b'data does\n\nmatter\nhere\n')
            _cmd(['git', 'add', fn])
            _cmd(['git', 'commit', '-m', 'v1'])
            _cmd(['git', 'tag', 'v1'])
            with open(fn, 'wb') as f:
                f.write(b'Brown fox\n')

            repo = git.Repo(td)
            v1 = repo.commit('v1')
            dres = diff.eval(v1, None)
            self.assertEqual(dres, {
                'lines': 5,
                'len': 1,
            })


if __name__ == '__main__':
    unittest.main()