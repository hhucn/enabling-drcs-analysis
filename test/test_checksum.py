import os.path
import sys
import tempfile
import unittest

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


class ChecksumTest(unittest.TestCase):
    def test_tree_checksums(self):
        import checksum

        with tempfile.TemporaryDirectory(suffix='test_checksum_') as td:
            os.mkdir(os.path.join(td, 'dir'))
            with open(os.path.join(td, 'filea'), 'wb') as f1:
                f1.write(b'foobar\xff\x00\xff')
            os.mkdir(os.path.join(td, 'dir2'))
            with open(os.path.join(td, 'dir2', 'fileb'), 'wb') as f1:
                f1.write(b'\x00' * 1000000)
            os.mkdir(os.path.join(td, 'dir2', 'dir3'))

            sums = checksum.tree_checksums(td)
            self.assertEqual(sums, {
                'filea': '4e696bddd90a6d75bb9c76f314e5e901e563828c9dbc9f51164660425af9e6eb',
                'dir2/fileb': 'd29751f2649b32ff572b5e0a9f541ea660a50f94ff0beedfb0b692b924cc8025',
                'dir': '(directory)',
                'dir2': '(directory)',
                'dir2/dir3': '(directory)',
            })


if __name__ == '__main__':
    unittest.main()
