import os.path
import sys
import unittest


sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


class UtilsTest(unittest.TestCase):
    def test_safe_filename(self):
        import utils

        self.assertEqual(utils.safe_filename('foo2/bar5-_'), 'foo2___bar5-_')

    def test_chunks(self):
        import utils

        self.assertEqual(list(utils.chunks('abcdefg', 2)), [
            ['a', 'b'],
            ['c', 'd'],
            ['e', 'f'],
            ['g'],
        ])
