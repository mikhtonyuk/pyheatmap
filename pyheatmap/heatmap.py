from PIL import Image, ImageChops
import math

class Heatmap:
    """Create heatmaps from a list of 2D coordinates"""

    def create(self, points, palette, size=None, dotsize=150, opacity=0.9, background=None):
        """
        points  -> an iterable list of tuples, where the contents are the 
                   x,y coordinates to plot. e.g., [(1, 1), (2, 2), (3, 3)]
                   3-value tuples can be used to specify point weight,
                   in this case weight should be float values in range [0, 1.0]
        palette -> an image with size (256, 1) that is used for color mapping
        size    -> tuple with the width, height in pixels of the output image 
        dotsize -> the size of a single coordinate in the output image in 
                   pixels, default is 150px.  Tweak this parameter to adjust 
                   the resulting heatmap.
        opacity -> the strength of a single coordiniate in the output image.  
                   Tweak this parameter to adjust the resulting heatmap.
        background -> background image or color tuple
        dotweight -> defines the alpha weight of single dot
        """
        if not size and (not background or not isinstance(background, Image.Image)):
            raise Exception("Either size or background image should be specified")

        self.points = points
        self.dotsize = dotsize
        self.opacity = opacity
        self.size =  background.size if background else size
        self.palette = self._loadPalette(palette)
        self.background = background or (255,255,255)

        dot = self._buildDot(self.dotsize)
        mask = self._buildMask(dot)

        res = self._colorize(mask)
        bg = self._getBackgroundImg()
        return res if not bg else Image.composite(res, bg, res)

    def _loadPalette(self, palette):
        """
        Reads color data from palette image
        """
        
        pl = Image.open(palette)
        pl = pl.convert("RGBA")
        
        assert(pl and pl.size == (256, 1))

        stops = []
        for i in range(256):
            stops.append( pl.getpixel((i, 0)) )

        return stops

    def _buildDot(self, size):
        """ 
        Builds a dot mask that is used for plotting
            each point in the dataset
        """
    
        img = Image.new("L", (size, size))
        pix = img.load()
        
        center = (size / 2.0)
        r_rec = 1.0 / math.sqrt( center * center )
        
        for x in range(size):
            for y in range(size):
                dx = x - center
                dy = y - center
                d = math.sqrt( dx * dx + dy * dy )
                c = 255 - int( 255 * d * r_rec )
                pix[x,y] = c
            
        return img

    def _buildMask(self, dot):
        """
        Creates the 'splatted' image
        """
        
        mask = Image.new('L', self.size)
        ds_2 = dot.size[0] / 2;
        
        for pnt in self.points:
            x = int(pnt[0] * self.size[0])
            y = int((1.0 -pnt[1]) * self.size[1])
            w = pnt[2] if len(pnt) > 2 else 1.0
            
            box = (x - ds_2, y - ds_2, x - ds_2 + self.dotsize, y - ds_2 + self.dotsize)
            
            region = mask.crop(box)
            weight = ImageChops.constant(region, int(w * 255))
            mdot = ImageChops.multiply(dot, weight)
            region = ImageChops.add(region, mdot)
            mask.paste(region, box)

        return mask

    def _colorize(self, mask):
        """ 
    Use the colorscheme selected to color the 
        image densities
    """

        mask = mask.load()

        img = Image.new("RGBA", self.size)
        pix = img.load()
        
        w,h = img.size
        for x in range(w):
            for y in range(h):
                strength = mask[x, y]
                r, g, b, a = self.palette[strength]

                # measure for palettes with no alpha
                a = int(a * self.opacity) if strength > 0 else 0
                
                rgba = (r, g, b, a)
                pix[x,y] = rgba

        return img

    def _getBackgroundImg(self):
        """
        Creates or reuses backgroung image based on type of input parameters
        """
        if self.background:
            if isinstance(self.background, Image.Image):
                return self.background
            elif isinstance(self.background, tuple):
                return Image.new("RGBA", self.size, self.background)
        return None


if __name__ == '__main__':
    import sys, argparse
    
    def read_stream(s):
        while True:
            l = s.readline().strip()
            if not l:
                break
            
            vals = map(float, l.split(','))
            yield tuple(vals)
    
    def read_csv(filenames):
        for fname in filenames:
            with open(fname, 'r') as f:
                for v in read_stream(f):
                    yield v
    
    parser = argparse.ArgumentParser(description='Draws heatmaps from CSV files or stdin')
    parser.add_argument('--palette', dest="palette", help="palette file for color mapping", default='resources/palette.png')
    parser.add_argument('--bg', dest="background", help="background file name")
    parser.add_argument('--size', dest="size", help="size of image h,w if not using background", default="800,600")
    parser.add_argument('--dotsize', dest="dotsize", help="size of the heat dot", default=100, type=int)
    parser.add_argument('--opacity', dest="opacity", help="opacity of the heat layer", default=0.9, type=float)
    parser.add_argument('--out', dest="output", help="specifies output file name", default="heatmap.jpg")
    parser.add_argument('file', nargs='*', help="the source CSV file")

    args = parser.parse_args()
    size = tuple(map(int, args.size.split(',')))
    
    if args.background:
        args.background = Image.open(args.background)
    
    points = read_csv(args.file) if args.file else read_stream(sys.stdin)
    
    try:
        img = Heatmap().create(points=points, palette=args.palette, size=size,\
                               dotsize=args.dotsize or None, opacity=args.opacity,\
                               background=args.background)
        
        img.save(args.output, 'JPEG')
    except KeyboardInterrupt:
        pass


