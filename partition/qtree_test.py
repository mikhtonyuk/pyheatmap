from qtree import *
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
    
    @patch('qtree2.QuadTreeVisitor')
    def testVisitor(self, MockVisitor):
        qt = QuadTree()
        qt._root = QuadBranch(qt, Rect.INF)
        for i in range(4):
            qt._root._children[i] = QuadLeaf(qt._root, Rect.INF)
        
        visitor = MockVisitor()
        qt.accept(visitor)
        
        self.assertListEqual([call.enterBranch(qt._root),\
                              call.visitLeaf(qt._root._children[0]),\
                              call.visitLeaf(qt._root._children[1]),\
                              call.visitLeaf(qt._root._children[2]),\
                              call.visitLeaf(qt._root._children[3]),\
                              call.leaveBranch(qt._root)], visitor.mock_calls)
    
    def testDepth(self):
        qt = QuadTree((0,0,10,10), max_items=1)
        items = set([(3,3),(7,7),(3,7),(7,3)])
        
        for i in items:
            qt.insert(i)
        
        self.assertEqual(qt.depth, 2)
        self.assertSetEqual(set(qt.items), items)
    
    def testItemsGenerator(self):
        r = QuadBranch(None, (0,0,10,10))
        r._children[1] = QuadLeaf(r, Rect((0,5,5,10)))
        r._children[3] = QuadLeaf(r, Rect((5,0,10,5)))
        r._children[1].insert((3,7), 1)
        r._children[1].insert((3,7), 2)
        r._children[3].insert((7,3), 3)
        
        items = list(r.items)
        self.assertListEqual(items, [1,2, 3])
    
    def testSimpleInsertWithoutSplitting(self):
        qt = QuadTree((0,0,10,10))
        self.assertTrue(qt.insert((5,5)))
        self.assertFalse(qt.insert((15,5)))




