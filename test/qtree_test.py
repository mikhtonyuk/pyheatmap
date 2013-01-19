from pyheatmap.partition.qtree import *
from mock import patch, call

import unittest

#====================================================

class QuedTreeTest(unittest.TestCase):
    def testQuater(self):
        r = Rect((-10,-10,10,10))
        self.assertEqual(Quater.ofArea(r, Quater.SW), (-10, -10,  0,  0))
        self.assertEqual(Quater.ofArea(r, Quater.NW), (-10,   0,  0, 10))
        self.assertEqual(Quater.ofArea(r, Quater.NE), (  0,   0, 10, 10))
        self.assertEqual(Quater.ofArea(r, Quater.SE), (  0, -10, 10,  0))
    
    def testCreate(self):
        qt = QuadTree((0,0,10,10))
        
        self.assertEqual(qt.area, (0,0,10,10))
        self.assertEqual(qt.root.quater, Quater.ROOT)
        self.assertEqual(qt.root.area, (0,0,10,10))
    
    @patch('pyheatmap.partition.qtree.QuadTreeVisitor')
    def testVisitor(self, MockVisitor):
        qt = QuadTree()
        qt._root = QuadBranch(qt, Rect.INF)
        for i in range(4):
            qt._root._children[i] = QuadLeaf(qt._root, Rect.INF)
        
        visitor = MockVisitor()
        visitor.enterBranch.return_value = True
        qt.accept(visitor)
        
        self.assertListEqual([call.enterBranch(qt._root),\
                              call.visitLeaf(qt._root._children[0]),\
                              call.visitLeaf(qt._root._children[1]),\
                              call.visitLeaf(qt._root._children[2]),\
                              call.visitLeaf(qt._root._children[3]),\
                              call.leaveBranch(qt._root)], visitor.mock_calls)
    
    def testSimpleInsertWithoutSplitting(self):
        qt = QuadTree((0,0,10,10))
        self.assertTrue(qt.insert((5,5)))
        self.assertFalse(qt.insert((15,5)))
        self.assertEqual(qt.count, 1)
    
    def testMaxItemsSplitting(self):
        qt = QuadTree((0,0,1,1), max_items=2)
        self.assertEqual(qt.depth, 1)
        
        qt.insert((0.1,0.1))
        self.assertEqual(qt.depth, 1)
        
        qt.insert((0.1,0.3))
        self.assertEqual(qt.depth, 1)
        
        # cascade split
        qt.insert((0.3,0.3))
        self.assertEqual(qt.depth, 3)
        
        qt.insert((0.7,0.7))
        self.assertEqual(qt.depth, 3)
    
    def testMaxDepth(self):
        qt = QuadTree((0,0,1,1), max_items=1, max_depth=3)
        
        import random
        for _ in range(100):
            x,y = random.random(), random.random()
            qt.insert((x,y))
        
        self.assertEqual(qt.depth, 3)
    
    def testMinSize(self):
        qt = QuadTree((0,0,1,1), max_items=1, min_size=0.4)
        
        import random
        for _ in range(100):
            x,y = random.random(), random.random()
            qt.insert((x,y))
        
        self.assertEqual(qt.depth, 2)
    
    def testItemRemoval(self):
        qt = QuadTree((0,0,1,1))
        qt.insert((0.1,0.1))
        qt.insert((0.9,0.9))
        
        self.assertEqual(qt.count, 2)
        
        self.assertTrue(qt.remove((0.9,0.9)))
        self.assertEqual(qt.count, 1)
        self.assertListEqual(list(qt.items), [(0.1,0.1)])
    
    def testMergeOnRemove(self):
        qt = QuadTree((0,0,1,1), max_items=2, min_items=2)
        qt.insert((0.1,0.1))
        qt.insert((0.4,0.4))
        qt.insert((0.3,0.3))
        self.assertEqual(qt.depth, 3)
        
        qt.remove((0.4,0.4))
        self.assertEqual(qt.depth, 1)



