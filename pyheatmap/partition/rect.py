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
    
    @property
    def width(self):
        return self._r[2] - self._r[0]
    
    @property
    def height(self):
        return self._r[3] - self._r[1]
    
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