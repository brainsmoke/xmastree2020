def xmaslight():
    # This is the code from my 
    
    #NOTE THE LEDS ARE GRB COLOUR (NOT RGB)
    
    # Here are the libraries I am currently using:
    import time
    import board
    import neopixel
    import re
    import math
    
    # You are welcome to add any of these:
    # import random
    # import numpy
    # import scipy
    # import sys
    
    # If you want to have user changable values, they need to be entered from the command line
    # so import sys sys and use sys.argv[0] etc
    # some_value = int(sys.argv[0])
    
    # IMPORT THE COORDINATES (please don't break this bit)
    
    coordfilename = "Python/coords.txt"
    
    fin = open(coordfilename,'r')
    coords_raw = fin.readlines()
    
    coords_bits = [i.split(",") for i in coords_raw]
    
    coords = []
    
    for slab in coords_bits:
        new_coord = []
        for i in slab:
            new_coord.append(int(re.sub(r'[^-\d]','', i)))
        coords.append(new_coord)
    
    #set up the pixels (AKA 'LEDs')
    PIXEL_COUNT = len(coords) # this should be 500
    
    pixels = neopixel.NeoPixel(board.D18, PIXEL_COUNT, auto_write=False)
    
    
    # YOU CAN EDIT FROM HERE DOWN

    # pause between cycles (normally zero as it is already quite slow)
    slow = 0
    
    # scale down to within unit sphere
    coords = [ (x/500., y/500., z/500.) for x,y,z in coords ]

    gamma = 2.2
    factor = 255 / (255**gamma)
    gamma_map = [ int( (x**gamma * factor + .5) ) for x in range(256) ]

    def led_color(color):
        r, g, b = color
        r = max(0, min(255, int(r)))
        g = max(0, min(255, int(g)))
        b = max(0, min(255, int(b)))
        return [gamma_map[g],gamma_map[r],gamma_map[b]]

    def light(color, dist):
        """ color at distance x """
        return tuple( float(x*dist*dist) for x in color )

    def dist_sq(a,b):
        ax,ay,az=a
        bx,by,bz=b
        dx,dy,dz=ax-bx,ay-by,az-bz
        return dx*dx+dy*dy+dz*dz

    def shader(color, a, b):
        d2 = dist_sq(a,b)
        r, g, b = color
        return r/d2, g/d2, b/d2

    class Attractor:
        def __init__(self, pos, color):
            self.pos = pos
            self.color = color

        def next(self):
            sigma, rho, beta = 10., 28., 8/3.
            dt = 1/1000.
            x, y, z = self.pos
            for i in range(10):
                dx, dy, dz = sigma*(y-x)*dt, (x*(rho-z)-y)*dt, (x*y-beta*z)*dt
                x, y, z = x+dx, y+dy, z+dz
            self.pos = (x,y,z)

    class LorenzAni:

        def __init__(self, coords):
            self.coords = [ (x*35,y*35,z*23+15) for x,y,z in coords ]
            #self.coords = [ (x*.11,y*.11,z*.11) for x,y,z in coords ]
            self.buf = [ [0.,0.,0.] for x in range(len(coords)) ]
            self.attractors = [ Attractor( (1,1,.5), light( (255, 32, 127), 5 ) ) ,
                                Attractor( (1,20,.5), light( (255, 255, 63), 5 ) ) ,
                                Attractor( (10,-40,0), light( (0, 0, 255), 5 ) ) ]

        def clear(self):
            for c in self.buf:
                c[0] = c[1] = c[2] = 0.

        def next(self):
            self.clear()
            for a in self.attractors:
                a.next()
                for i,pos in enumerate(self.coords):
                    ri,gi,bi = shader(a.color, pos, a.pos)
                    self.buf[i][0]+=ri
                    self.buf[i][1]+=gi
                    self.buf[i][2]+=bi

    ani = LorenzAni(coords)

    while True:
        time.sleep(slow)
        ani.next()
        for i, color in enumerate(ani.buf):
            pixels[i] = led_color(color)
        pixels.show()
        
    return 'DONE'


# yes, I just put this at the bottom so it auto runs
xmaslight()
