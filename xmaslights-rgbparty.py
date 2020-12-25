
# I'm guessing this is no problem either :-P
import cmath


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

    def dist_sq(a,b):
        ax,ay,az=a
        bx,by,bz=b
        dx,dy,dz=ax-bx,ay-by,az-bz
        return dx*dx+dy*dy+dz*dz

    def phase(a,b):
        return (cmath.phase(a+1j*b)/math.pi/2 * 2048) % 2048

    class GradientAni:

        def __init__(self, coords):
            self.coords = [ (phase(y,z), phase(z,x), phase(x,y)) for x,y,z in coords ]
            self.buf = [ [0.,0.,0.] for x in range(len(coords)) ]
            self.rotation = [0,0,0]

        def clear(self):
            for c in self.buf:
                c[0] = c[1] = c[2] = 0.

        def next(self):
            self.clear()
            ri, rj, rk = self.rotation
            self.rotation = (ri+15)%2048, (rj+13)%2048, (rk+19)%2048
            for i, rot in enumerate(self.coords):
                di, dj, dk = rot
                if (ri+di)%1024 < 128:
                    self.buf[i][0]=255
                if (rj+dj)%1024 < 128:
                    self.buf[i][1]=255
                if (rk+dk)%1024 < 128:
                    self.buf[i][2]=255

    ani = GradientAni(coords)

    while True:
        time.sleep(slow)
        ani.next()
        for i, color in enumerate(ani.buf):
            pixels[i] = led_color(color)
        pixels.show()
        
    return 'DONE'


# yes, I just put this at the bottom so it auto runs
xmaslight()
