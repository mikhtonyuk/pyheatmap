from pyheatmap.partition.grid import *
import unittest

class GridTest(unittest.TestCase):
    def testCreateFromCellsNumber(self):
        grid = Grid((0,0,1,1), cells_num=(2,4))
        self.assertEqual(grid.dimensions, (2,4))
    
    def testCreateFromCellsSize(self):
        grid = Grid((0,0,1,1), cell_size=(0.5, 0.25))
        self.assertEqual(grid.dimensions, (2,4))
    
    def testInsert(self):
        grid = Grid((0,0,1,1), cells_num=(2,4))
        where = grid.insert((0.7,0.9))
        
        self.assertEqual(where, (1,3))
        self.assertEqual(grid[where].count, 1)
    
    def testRemove(self):
        grid = Grid((0,0,1,1), cells_num=(2,4))
        grid.insert((0.1,0.3))
        self.assertEqual(grid.count, 1)
        
        where = grid.remove((0.9,0.9))
        self.assertIsNone(where)
        
        where = grid.remove((0.1,0.3))
        self.assertEqual(where, (0,1))
        self.assertEqual(grid.count, 0)