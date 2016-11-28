import os.path
import sys
import unittest

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


class ResultStatsTest(unittest.TestCase):
    def test_rank_calc(self):
        import print_result_stats

        self.assertEqual(
            print_result_stats.calc_rank({'a': 1, 'b': 3, 'c': 2}),
            {'a': 0, 'c': 1, 'b': 2})
        self.assertEqual(
            print_result_stats.calc_rank({'a': 1, 'b': 1, 'c': 19, 'd': 15, 'e': 19, 'f': 19}),
            {'a': 0.5, 'b': 0.5, 'd': 2, 'c': 4, 'e': 4, 'f': 4})


if __name__ == '__main__':
    unittest.main()
