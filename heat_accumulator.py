from partition.qtree import QuadTree, InsertionVisitor
import sys

#====================================================

class HeatAccumulatingInserter(InsertionVisitor):
    def finalInsert(self, leaf, p, item):
        leaf.insert(item)
        # for leaf node that will never split collapse all items into one
        if leaf.area.width * 0.5 < self.min_size or leaf.area.height * 0.5 < self.min_size:
            merged = self.mergeItems(leaf.items)
            leaf.clear()
            leaf.insert(merged)
    
    def mergeItems(self, items):
        # weighted average of coords and sum of weights
        X, Y, W = 0, 0, 0
        for x,y,w in items:
            X += x * w
            Y += y * w
            W += w
        
        iW = 1.0 / W
        return (X * iW, Y * iW, W)

#====================================================

if __name__ == '__main__':
    def read_stream(s):
        while True:
            l = s.readline().strip()
            if not l:
                break
            
            vals = map(float, l.split(','))
            if len(vals) == 2:
                vals.append(1.0)
            if len(vals) != 3:
                raise Exception("Invalid data length: %s" % (l))
            yield tuple(vals)
    
    def read_csv(filenames):
        for fname in filenames:
            with open(fname, 'r') as f:
                for v in read_stream(f):
                    yield v
    
    
    import argparse
    parser = argparse.ArgumentParser(description='Accumulates events heat with specified precision and outputs the result')
    parser.add_argument('--area', dest="area", help="bounding rect of even coordinates (x0,y0,x1,y1)", default='0,0,1,1')
    parser.add_argument('--error', dest="error", help="maximum error allowed", type=float, default=0.001)
    parser.add_argument('--out', dest="output", help="specifies output file name", default=None)
    parser.add_argument('file', nargs='*', help="the source CSV file")
    
    args = parser.parse_args()
    area = tuple(map(float, args.area.split(',')))
    out = args.output or sys.stdout
    points = read_csv(args.file) if args.file else read_stream(sys.stdin)
    
    try:
        qt = QuadTree(area, lambda x: (x[0],x[1]), min_size=args.error, inserter=HeatAccumulatingInserter)
        for p in points:
            qt.insert(p)
        print qt
    except KeyboardInterrupt:
        pass




