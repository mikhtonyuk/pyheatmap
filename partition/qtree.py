from sys import float_info

#====================================================

# TODO: Optimize creation
class Rect(object):
    INF = None
    
    def __init__(self, tpl):
        if isinstance(tpl, Rect):
            self._r = tpl._r
        elif isinstance(tpl, tuple):
            self._r = tuple(map(float, tpl))
        else:
            raise ValueError("Cant create rect from %s" % (tpl))
        self.validate()
    
    def validate(self):
        if self._r[0] > self._r[2] or self._r[1] > self._r[3]:
            raise Exception("Invalid rect %s" % (self._r))
    
    def contains(self, p):
        r = self._r
        return p[0] >= r[0] and p[0] <= r[2] and p[1] >= r[1] and p[1] <= r[3]
    
    def __eq__(self, tpl):
        other = Rect(tpl)
        for i in range(4):
            if abs(self._r[i] - other._r[i]) > 0.0001:
                return False
        return True
    
    def __neq(self, tpl):
        return not self.__eq__(tpl)
    
    def __str__(self):
        return str(self._r)
    
    def __repr__(self):
        return 'rect'+str(self)
    
    def __iter__(self):
        return iter(self._r)
    
    def __getitem__(self, i):
        return self._r[i]

setattr(Rect, 'INF', Rect((float_info.min, float_info.min, float_info.max, float_info.max)))

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
    
    def insert(self, p, item):
        assert self.area.contains(p)
        self._items.append(item)
    
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
    
    @property
    def children(self):
        return self._children
    
    @property
    def items(self):
        return (i for c in self._children for i in c.items)
    
    def accept(self, visitor):
        visitor.enterBranch(self)
        for c in self._children:
            if c:
                c.accept(visitor)
        visitor.leaveBranch(self)
    
    def __str__(self):
        return "branch [%s] area %s" % (Quater.toString(self.quater), self.area)

#====================================================

class QuadTree(object):
    def __init__(self, rect=None, getcoord = None, max_items=1000, max_depth=0):
        self.max_items = max_items
        self.max_depth = max_depth
        
        self._getcoord = getcoord or (lambda x: x)
        self._root = QuadLeaf(self, Rect(rect) if rect else Rect.INF)
        self._inserter = InsertionVisitor(self._getcoord, self.max_items, self.max_depth)
    
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
    def depth(self):
        v = DepthProbeVisitor()
        self.accept(v)
        return v.max_depth + 1
    
    def insert(self, item):
        self._inserter.init(item)
        self.accept(self._inserter)
        return self._inserter.depth + 1
    
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
    
    def __str__(self):
        v = PrinterVisitor()
        self.accept(v)
        return v.str

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
        self.depth = -1
        self.max_depth = 0
    
    def enterBranch(self, branch):
        self.depth += 1
        return True
    
    def leaveBranch(self, branch):
        self.depth -= 1
    
    def visitLeaf(self, leaf):
        self.max_depth = max(self.max_depth, self.depth + 1)

#====================================================

class InsertionVisitor(QuadTreeVisitor):
    def __init__(self, get_cord, max_items=0, max_depth=0):
        self.depth = -1
        self.item = None
        
        self.get_cord = get_cord
        self.max_items = max_items
        self.max_depth = max_depth
    
    def init(self, item):
        self.depth = -1
        self.p = self.get_cord(item)
        self.item = item
    
    def enterBranch(self, branch):
        self.depth += 1
        return self.p and branch.area.contains(self.p)
    
    def leaveBranch(self, branch):
        self.depth -= 1
    
    def visitLeaf(self, leaf):
        self.depth += 1
        if leaf.area.contains(self.p):
            self.splitInsert(leaf)
            raise StopIteration()
        self.depth -= 1
    
    def splitInsert(self, leaf):
        if self.max_items and len(leaf.items) >= self.max_items\
        and (not self.max_depth or self.depth < self.max_depth):
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
                    q.insert(p, i)
                    break
        
        return br
    
    def finalInsert(self, leaf, p, item):
        leaf.insert(p, item)

#====================================================

class PrinterVisitor(QuadTreeVisitor):
    def __init__(self):
        self.depth = -1
        self.str = ""

    def enterBranch(self, branch):
        self.depth += 1
        self.str += "%s %s\n" % ('\t'*self.depth, branch)
        return True

    def leaveBranch(self, branch):
        self.depth -= 1

    def visitLeaf(self, leaf):
        self.str += "%s %s\n" % ('\t'*(self.depth+1), leaf)
        self.str += '\t'*(self.depth+2) + str(leaf.items) + '\n'

