from rect import Rect

#====================================================

class GridCell(object):
    def __init__(self, grid, coords):
        self.grid = grid
        self.coords = coords
        self.items = []
    
    @property
    def index(self):
        return self.coords
    
    @property
    def count(self):
        return len(self.items)
    
    def insert(self, item):
        self.items.append(item)
    
    def remove(self, item):
        try:
            self.items.remove(item)
            return True
        except ValueError:
            return False
    
    def clear(self):
        self.items = []

#====================================================

class Grid(object):
    def __init__(self, area, getcoord = lambda x: x, cell_size=None, cells_num=None):
        """Grid space partition"""
        
        if (cell_size is None and cells_num is None) \
        or (cell_size is not None and cells_num is not None):
            raise Exception('Specify either cell_size or cells_number')
        
        self.area = Rect(area)
        self._getcoord = getcoord
        
        if cells_num is not None:
            self._cells = self._createGridFromNum(cells_num)
        else:
            self._cells = self._createGridFromAreaAndSize(self.area, cell_size)
    
    @property
    def dimensions(self):
        return (len(self._cells[0]), len(self._cells))
    
    @property
    def cells(self):
        return (c for cy in self._cells for c in cy)
    
    @property
    def items(self):
        return (i for c in self.cells for i in c.items)
    
    @property
    def count(self):
        return sum( (c.count for c in self.cells) )
    
    def __getitem__(self, xy):
        return self._cells[xy[1]][xy[0]]
    
    def insert(self, item):
        cell = self.getCell(self._getcoord(item))
        if not cell:
            return None
        cell.insert(item)
        return cell.index
    
    def remove(self, item):
        cell = self.getCell(self._getcoord(item))
        if not cell:
            return None
        return cell.index if cell.remove(item) else None
    
    def clear(self):
        self._cells = self._createGridFromNum(self.dimensions)
    
    def getCell(self, coords):
        x,y = coords
        nx,ny = self.dimensions
        
        cx = int((x - self.area[0]) / self.area.width * nx)
        cy = int((y - self.area[1]) / self.area.height * ny)
        
        if cx < 0 or cx >= nx or cy < 0 or cy >= ny:
            return None
        return self[cx, cy]
    
    def _createGridFromNum(self, cells_num):
        cn = None
        if isinstance(cells_num, tuple) and cells_num[0] > 0 and cells_num[1] > 0:
            cn = cells_num
        elif isinstance(cells_num, int) and cells_num > 0:
            cn = (cells_num, cells_num)
        else:
            raise Exception('Cells number should be tuple or int')
        
        grid = [ [ GridCell(self, (x,y)) for x in range(cn[0]) ] for y in range(cn[1])]
        return grid
    
    def _createGridFromAreaAndSize(self, area, cell_size):
        cs = None
        if isinstance(cell_size, tuple) and cell_size[0] > 0 and cell_size[1] > 0:
            cs = cell_size
        elif (isinstance(cell_size, int) or isinstance(cell_size, float)) and cell_size > 0:
            cs = (float(cell_size), float(cell_size))
        else:
            raise Exception('Cells size should be tuple or float')
        
        cnx = int(round(area.width / cs[0]))
        cny = int(round(area.height / cs[1]))
        return self._createGridFromNum((cnx, cny))
    
    def __str__(self):
        ret = 'grid %dx%d:' % self.dimensions
        return ret





