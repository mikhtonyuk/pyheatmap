from partition.grid import Grid
import sys

#====================================================

class HeatGrid(Grid):
    def insert(self, item):
        where = Grid.insert(self, item)
        if where:
            cell = self[where]
            merged = self.mergeItems(cell.items)
            cell.clear()
            cell.insert(merged)
    
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
    parser.add_argument('--area', dest="area", help="bounding rect of event coordinates (x0,y0,x1,y1)", default='0,0,1,1')
    parser.add_argument('--grid', dest="grid", help="Number of x,y grid cells for subdivision", default='100,100')
    parser.add_argument('--error', dest="error", help="maximum error allowed", type=float, default=None)
    parser.add_argument('file', nargs='*', help="the source CSV file")
    
    args = parser.parse_args()
    area = tuple(map(float, args.area.split(',')))
    dims = tuple(map(int, args.grid.split(','))) if not args.error else None
    error = args.error
    points = read_csv(args.file) if args.file else read_stream(sys.stdin)
    
    try:
        grid = HeatGrid(area, lambda x: (x[0],x[1]), cell_size=error, cells_num=dims)
        
        for p in points:
            grid.insert(p)
        
        max_heat = max([i[2] for i in grid.items])
        
        for p in grid.items:
            x,y,w = p
            print '%s,%s,%s' % (x,y,w/max_heat)
        
    except KeyboardInterrupt:
        pass




