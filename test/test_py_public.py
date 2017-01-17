import os
import re
import unittest


class PyPublicTest(unittest.TestCase):
    def test_py_public(self):
        root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        py_files = sorted(
            fn for fn in os.listdir(root_dir)
            if fn.endswith('.py'))

        public_fn = os.path.join(root_dir, '.public')
        with open(public_fn, 'r', encoding='utf-8') as public_f:
            lines = public_f.read().split('\n')

        public_py_files = sorted(
            line for line in lines
            if re.match(r'^\s*[^#][a-z0-9_-]+\.py', line))

        self.assertEquals(py_files, public_py_files)


if __name__ == '__main__':
    unittest.main()
