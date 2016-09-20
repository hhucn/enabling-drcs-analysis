import os.path
import sys
import unittest


sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

#    /-B-D---\
# A-<   \ \   >-F
#    \---C-E-/
#
# G--H

CD = {
    'A': {'parents': ['B', 'C']},
    'B': {'parents': ['C', 'D']},
    'C': {'parents': ['E']},
    'D': {'parents': ['E', 'F']},
    'E': {'parents': ['F']},
    'F': {'parents': []},
    'G': {'parents': ['H']},
    'H': {'parents': []},
}
for k, v in CD.items():
    v['sha'] = k


class GraphTest(unittest.TestCase):
    def test_calc_depths(self):
        import graph

        graph.calc_depths(CD)
        self.assertEqual(CD['A']['depth'], 4)
        self.assertEqual(CD['B']['depth'], 3)
        self.assertEqual(CD['C']['depth'], 2)
        self.assertEqual(CD['D']['depth'], 2)
        self.assertEqual(CD['E']['depth'], 1)
        self.assertEqual(CD['F']['depth'], 0)
        self.assertEqual(CD['G']['depth'], 1)
        self.assertEqual(CD['H']['depth'], 0)

    def test_calc_sizes(self):
        import graph
        return
        graph.calc_children(CD)
        graph.calc_sizes(CD)
        self.assertEqual(CD['A']['size'], 5)
        self.assertEqual(CD['B']['size'], 4)
        self.assertEqual(CD['C']['size'], 2)
        self.assertEqual(CD['D']['size'], 3)
        self.assertEqual(CD['E']['size'], 2)
        self.assertEqual(CD['F']['size'], 1)
        self.assertEqual(CD['G']['size'], 2)
        self.assertEqual(CD['H']['size'], 1)
