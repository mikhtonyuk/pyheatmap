
class NodeType(object):
    SECTION = 0
    TERMINAL = 1

#====================================================

class Quater(object):
    NE = 0
    SE = 1
    SW = 2
    NW = 3
    ROOT = 4
    
    str2quater = { 'NE' : 0, 'SE' : 1, 'SW' : 2, 'NW' : 3, 'ROOT' : 4 }
    quater2str = ['NE', 'SE', 'SW', 'NW', 'ROOT']
    
    @staticmethod
    def toString(q):
        return Quater.quater2str[q]
    
    @staticmethod
    def fromString(s):
        return Quater.str2quater[s]

#====================================================

class QuadNode(object):
    
    def __init__(self, tree, t, area, quater, parent):
        self.Tree = tree
        self.Type = t
        self.Area = area
        self.Quater = quater
        self.Parent = parent
    
    def Accept(self, visitor):
        pass

#====================================================

class QuadSection(QuadNode):
    
    def __init__(self, tree, area, quater, parent):
        QuadNode.__init__(self, tree, NodeType.SECTION, area, quater, parent)
        self.Quaters = None
    
    def isEmpty(self):
        return self.Quaters is None
    
    def Accept(self, visitor):
        if visitor.EnterSection(self) and self.Quaters is not None:
            for q in self.Quaters:
                q.Accept(visitor)
        visitor.LeaveSection(self)
    
    def Split(self, force_type=None):
        term = self.Tree.getTerminalSize()
        area = self.Area
        w2 = area[2] * 0.5
        h2 = area[3] * 0.5
        
        aNE = (area[0]+w2, area[1], w2, h2)
        aSE = (area[0]+w2, area[1]+h2, w2, h2)
        aSW = (area[0], area[1]+h2, w2, h2)
        aNW = (area[0], area[1], w2, h2)
        
        QType = force_type if force_type else (QuadTerminal if (w2 <= term and h2 <= term) else QuadSection)
        
        self.Quaters = ( \
            QType(self.Tree, aNE, Quater.NE, self), \
            QType(self.Tree, aSE, Quater.SE, self), \
            QType(self.Tree, aSW, Quater.SW, self), \
            QType(self.Tree, aNW, Quater.NW, self), \
            )
    
    def __str__(self):
        return "section [%s] area %s" % (Quater.toString(self.Quater), self.Area)

#====================================================

class QuadTerminal(QuadNode):
    
    def __init__(self, tree, area, quater, parent):
        QuadNode.__init__(self, tree, NodeType.TERMINAL, area, quater, parent)
        self.Items = []
    
    def Accept(self, visitor):
        visitor.VisitTerminal(self)
    
    def __str__(self):
        return "terminal [%s] area %s" % (Quater.toString(self.Quater), self.Area)

#====================================================

class QuadTreeVisitor(object):
    
    def EnterSection(self, section):
        return True
    
    def LeaveSection(self, section):
        pass
    
    def VisitTerminal(self, terminal):
        pass

#====================================================


class QuadTreeInserter(QuadTreeVisitor):
    
    def __init__(self, item):
        self.Item = item
        self.Place = None
    
    def __inArea(self, area, pos):
        x = pos[0] - area[0];
        y = pos[1] - area[1];
        return x >= 0 and y >= 0 and x < area[2] and y < area[3];
    
    def EnterSection(self, section):
        if not self.__inArea(section.Area, section.Tree.Agent(self.Item)):
            return False
        elif section.isEmpty():
            section.Split()
        return self.Place is None
    
    def LeaveSection(self, section):
        pass
    
    def VisitTerminal(self, terminal):
        if self.__inArea(terminal.Area, terminal.Tree.Agent(self.Item)):
            terminal.Items.append(self.Item)
            self.Place = terminal

#====================================================

class QuadTreePrinter(QuadTreeVisitor):
    
    def __init__(self):
        self.depth = -1
        self.str = ""

    def EnterSection(self, section):
        self.depth += 1
        self.str += "%s %s\n" % ('\t'*self.depth, section)
        return True

    def LeaveSection(self, section):
        self.depth -= 1

    def VisitTerminal(self, terminal):
        self.str += "%s %s\n" % ('\t'*(self.depth+1), terminal)
        self.str += '\t'*(self.depth+2) + str(terminal.Items) + '\n'

#====================================================

class QuadTree(object):
    
    def __init__(self, area, terminal_size, agent):
        self.Agent = agent
        self.Root = QuadSection(self, area, Quater.ROOT, None)
        self.terminal_size = terminal_size
    
    def getTerminalSize(self):
        return self.terminal_size
    
    def setTerminalSize(self, value):
        self.terminal_size = value
        self.Clear()
    
    def Clear(self):
        self.Root = QuadSection(self, self.Root.Area, Quater.ROOT, None)
        pass
    
    def Insert(self, item):
        inserter = QuadTreeInserter(item)
        self.Accept(inserter)
    
    def Accept(self, visitor):
        self.Root.Accept(visitor)
    
    def __str__(self):
        p = QuadTreePrinter()
        self.Accept(p)
        return p.str

#====================================================

if __name__ == "__main__":
    qt = QuadTree( (0, 0, 8, 8), 1, lambda i: i )
    qt.Insert( (0.5, 0.5) )
    qt.Insert( (4.5, 4.5) )
    print qt

