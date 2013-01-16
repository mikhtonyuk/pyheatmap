from partition.qtree import Rect
import sys

#====================================================

def normalize_coords(points, area):
    area = Rect(area)
    winv = 1.0 / area.width
    hinv = 1.0 / area.height
    
    for p in points:
        if not area.contains(p):
            sys.stderr.write("Point %s falls outside of given area\n" % (tuple(p),))
        p[0] = (p[0] - area[0]) * winv
        p[1] = (p[1] - area[1]) * hinv
        yield tuple(p)

#====================================================

if __name__ == '__main__':
    def read_stream(s):
        while True:
            l = s.readline().strip()
            if not l:
                break
            
            vals = map(float, l.split(','))
            if len(vals) < 2 or len(vals) > 3:
                raise Exception("Invalid data length: %s" % (l))
            yield vals
    
    def read_csv(filenames):
        for fname in filenames:
            with open(fname, 'r') as f:
                for v in read_stream(f):
                    yield v
    
    
    import argparse
    parser = argparse.ArgumentParser(description='Normalizes input coords according to specified bounding rect')
    parser.add_argument('--area', dest="area", help="bounding rect of event coordinates (x0,y0,x1,y1)", default='0,0,1,1')
    parser.add_argument('file', nargs='*', help="the source CSV file")
    
    args = parser.parse_args()
    area = tuple(map(float, args.area.split(',')))
    points = read_csv(args.file) if args.file else read_stream(sys.stdin)
    
    try:
        for p in normalize_coords(points, area):
            print ','.join(map(str,p))
    except KeyboardInterrupt:
        pass




