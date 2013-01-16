from pyheatmap.mapcoords import normalize_coords
import unittest

class CoordTransformerTest(unittest.TestCase):
    def testNormalize(self):
        points = [[0.0,0.0], [5.0,5.0], [10.0,10.0]]
        norm = list(normalize_coords(points, (0.0, 0.0, 10.0, 10.0)))
        self.assertListEqual(norm, [(0.0,0.0),(0.5,0.5),(1.0,1.0)])
