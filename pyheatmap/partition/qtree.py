from rect import Rect

#====================================================

class Quater(object):
    """Assumes:
    Y ^
      | NW | NE
      | -- + --
      | SW | SE
      +-------->
               X
    """
    
    SW = 0
    NW = 1
    NE = 3
    SE = 2
    ROOT = 4
    
    str2quater = { 'SW' : 0, 'NW' : 1, 'NE' : 3, 'SE' : 2, 'ROOT' : 4 }
    quater2str = ['SW', 'NW', 'SE', 'NE', 'ROOT']
    
    @staticmethod
    def toString(q):
        return Quater.quater2str[q]
    
    @staticmethod
    def fromString(s):
        return Quater.str2quater[s]
    
    @staticmethod
    def ofArea(rect, q):
        x0,y0,x1,y1 = tuple(rect)
        w2 = (x1 - x0) * 0.5
        h2 = (y1 - y0) * 0.5
        
        x0 = x0 + w2 * ((q & 2) >> 1)
        y0 = y0 + h2 * (q & 1)
        return Rect( (x0, y0, x0 + w2, y0 + h2) )

#====================================================

class QuadNode(object):
    LEAF = 0
    BRANCH = 1
    
    def __init__(self, typ, parent, area):
        self.type = typ
        self.parent = parent
        self.area = area
    
    @property
    def quater(self):
        return self.parent._quater(self)

#====================================================

class QuadLeaf(QuadNode):
    def __init__(self, parent, area):
        QuadNode.__init__(self, QuadNode.LEAF, parent, area)
        self._items = []
    
    @property
    def items(self):
        return self._items
    
    @property
    def count(self):
        return len(self._items)
    
    def insert(self, item):
        self._items.append(item)
    
    def remove(self, item):
        try:
            self._items.remove(item)
            return True
        except ValueError:
            return False
    
    def clear(self):
        self._items = []
    
    def split(self):
        br = QuadBranch(self.parent, self.area)
        self.parent._wasSplit(self, br)
        return br
    
    def accept(self, visitor):
        visitor.visitLeaf(self)
    
    def __str__(self):
        return "leaf [%s] area %s" % (Quater.toString(self.quater), self.area)

#====================================================

class QuadBranch(QuadNode):
    def __init__(self, parent, area):
        QuadNode.__init__(self, QuadNode.BRANCH, parent, area)
        self._children = [QuadLeaf(self, Quater.ofArea(area, q)) for q in range(4)]
    
    def _quater(self, node):
        i = self._children.index(node)
        assert i >= 0
        return i
    
    def _wasSplit(self, leaf, br):
        q = self._quater(leaf)
        self._children[q] = br
    
    def _wasMerged(self, br, leaf):
        q = self._quater(br)
        self._children[q] = leaf
    
    @property
    def children(self):
        return self._children
    
    @property
    def items(self):
        return (i for c in self._children for i in c.items)
    
    @property
    def count(self):
        return sum( ( c.count for c in self._children ) )
    
    def clear(self):
        self._children = [QuadLeaf(self, Quater.ofArea(self.area, q)) for q in range(4)]
    
    def merge(self):
        leaf = QuadLeaf(self.parent, self.area)
        self.parent._wasMerged(self, leaf)
        return leaf
    
    def accept(self, visitor):
        if visitor.enterBranch(self):
            for c in self._children:
                if c:
                    c.accept(visitor)
            visitor.leaveBranch(self)
    
    def __str__(self):
        return "branch [%s] area %s" % (Quater.toString(self.quater), self.area)

#====================================================

class QuadTreeVisitor(object):
    
    def enterBranch(self, branch):
        return True
    
    def leaveBranch(self, branch):
        pass
    
    def visitLeaf(self, leaf):
        pass

#====================================================

class DepthProbeVisitor(object):
    def __init__(self):
        self.depth = 0
        self.max_depth = 0
    
    def enterBranch(self, branch):
        self.depth += 1
        return True
    
    def leaveBranch(self, branch):
        self.depth -= 1
    
    def visitLeaf(self, leaf):
        self.max_depth = max(self.max_depth, self.depth+1)

#====================================================

class InsertionVisitor(QuadTreeVisitor):
    def __init__(self, get_cord, max_items, max_depth, min_size):
        self.depth = 0
        self.item = None
        
        self.get_cord = get_cord
        self.max_items = max_items
        self.max_depth = max_depth
        self.min_size = min_size
    
    def init(self, item):
        self.depth = 0
        self.p = self.get_cord(item)
        self.item = item
    
    def enterBranch(self, branch):
        if branch.area.contains(self.p):
            self.depth += 1
            return True
        return False
    
    def leaveBranch(self, branch):
        self.depth -= 1
    
    def visitLeaf(self, leaf):
        self.depth += 1
        if leaf.area.contains(self.p):
            self.splitInsert(leaf)
            raise StopIteration()
        self.depth -= 1
    
    def splitInsert(self, leaf):
        if self.max_items and len(leaf.items) >= self.max_items \
        and (not self.max_depth or self.depth < self.max_depth) \
        and (not self.min_size or (leaf.area.width * 0.5 >= self.min_size and leaf.area.height * 0.5 >= self.min_size)):
            br = self.split(leaf)
            self.depth -= 1
            br.accept(self)
        else:
            self.finalInsert(leaf, self.p, self.item)
    
    def split(self, leaf):
        br = leaf.split()
        
        for i in leaf.items:
            p = self.get_cord(i)
            for q in br.children:
                if q.area.contains(p):
                    q.insert(i)
                    break
        
        return br
    
    def finalInsert(self, leaf, p, item):
        leaf.insert(item)

#====================================================

class RemovalVisitor(QuadTreeVisitor):
    def __init__(self, get_coord, min_items):
        self.depth = 0
        self.p = None
        self.item = None
        
        self.get_coord = get_coord
        self.min_items = min_items
    
    def init(self, item):
        self.depth = 0
        self.p = self.get_coord(item)
        self.item = item
    
    def enterBranch(self, branch):
        if branch.area.contains(self.p):
            self.depth += 1
            return True
        return False
    
    def leaveBranch(self, branch):
        self.depth -= 1
    
    def visitLeaf(self, leaf):
        self.depth += 1
        if leaf.area.contains(self.p):
            removed = self.mergeRemove(leaf)
            self.depth = self.depth if removed else 0
            raise StopIteration()
        self.depth -= 1
    
    def mergeRemove(self, leaf):
        removed = leaf.remove(self.item)
        
        if removed:
            while self.min_items and leaf.count <= self.min_items \
                                 and leaf.quater != Quater.ROOT \
                                 and leaf.parent.count <= self.min_items:
                parent = leaf.parent
                leaf = parent.merge()
                leaf._items.extend(parent.items)
        
        return removed

#====================================================

class PrinterVisitor(QuadTreeVisitor):
    def __init__(self):
        self.depth = -1
        self.str = ""

    def enterBranch(self, branch):
        self.depth += 1
        self.str += "%s%s\n" % ('  '*self.depth, branch)
        return True

    def leaveBranch(self, branch):
        self.depth -= 1

    def visitLeaf(self, leaf):
        self.str += "%s%s\n" % ('  '*(self.depth+1), leaf)
        self.str += "%s%s\n" % ('  '*(self.depth+2), leaf.items)

#====================================================

class QuadTree(object):
    def __init__(self, rect=None, getcoord = lambda x: x, 
                 max_items=100, max_depth=0, min_size=0, min_items=0,
                 inserter=InsertionVisitor, remover=RemovalVisitor):
        """QuadTree:
        rect - quad tree area limits (x0,y0,x1,y1)
        getcoord - callabe that extracts coordinates from items, should return (x,y)
        max_items - number of items in leaf node when it will be subdivided
        max_depth - limits tree depth
        min_size - limits tree by smallest area height or width
        min_items - number of items under lowest order branch node when it will be merged into leaf
        """
        
        self.max_items = max_items
        self.max_depth = max_depth
        self.min_size = min_size
        self.min_items = min_items
        
        self._getcoord = getcoord
        self._root = QuadLeaf(self, Rect(rect) if rect else Rect.INF)
        self._inserter = inserter(self._getcoord, self.max_items, self.max_depth, self.min_size)
        self._remover = remover(self._getcoord, self.min_items)
    
    @property
    def root(self):
        return self._root
    
    @property
    def area(self):
        return self._root.area
    
    @property
    def items(self):
        return self._root.items
    
    @property
    def count(self):
        return self._root.count
    
    @property
    def depth(self):
        v = DepthProbeVisitor()
        self.accept(v)
        return v.max_depth
    
    def insert(self, item):
        self._inserter.init(item)
        self.accept(self._inserter)
        return self._inserter.depth
    
    # TODO: optimize merging checks
    # TODO: add optimize method
    def remove(self, item):
        self._remover.init(item)
        self.accept(self._remover)
        return self._remover.depth != 0
    
    def clear(self):
        self._root = QuadLeaf(self, self.area)
    
    def accept(self, visitor):
        try:
            self._root.accept(visitor)
        except StopIteration:
            pass
    
    def _quater(self, node):
        assert node == self.root
        return Quater.ROOT
    
    def _wasSplit(self, leaf, br):
        assert leaf == self._root
        self._root = br
    
    def _wasMerged(self, br, leaf):
        assert br == self._root
        self._root = leaf
    
    def __str__(self):
        v = PrinterVisitor()
        self.accept(v)
        return v.str

#====================================================


