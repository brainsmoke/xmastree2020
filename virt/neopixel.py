
import sys, math, re, time

import pygame
pygame.init()

black = (0, 0, 0)

class VirtualDisplay(object):
    def __init__(self, pixels, windowsize=(720, 480), dotsize=6, inverse_gamma=2.5):
        self.w, self.h = windowsize
        self.dotsize = float(dotsize)/self.h
        self.pixels = pixels
        self.screen = pygame.display.set_mode(windowsize, pygame.RESIZABLE|pygame.DOUBLEBUF)
        pygame.key.set_repeat(500,25)
        self.screen.fill(black)
        self.gamma_map = tuple( int( (x/255.)**(1/inverse_gamma) * 255. ) for x in range(256) )

    def draw_led(self, surf, x, y, color, r):
         pygame.draw.circle(surf, color, (x, y), r)

    def render(self, data):
        surf = pygame.display.get_surface()
        r = int(self.dotsize*self.h/2.)

        for point, color in zip(self.pixels, data):
            color = ( self.gamma_map[color[1]], self.gamma_map[color[0]], self.gamma_map[color[2]] )
            x, y = point
            self.draw_led(surf, int(x*self.w), int(y*self.h), color, r)

    def check_events(self):
        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN:
                if event.unicode == 'q':
                    sys.exit(0)
            if event.type == pygame.QUIT:
                sys.exit(0)
            if event.type == pygame.VIDEORESIZE:
                self.screen = pygame.display.set_mode((event.w, event.h), pygame.RESIZABLE|pygame.DOUBLEBUF)
                self.w = event.w
                self.h = event.h

    def write(self, data):
        self.check_events()
        self.render(data)
        pygame.display.flip()
        self.screen.fill(black)

def load_points():
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

    return coords

def project(p):
    x,y,z = p
    return (.5+y/1200.,.5-z/1200,x)

class NeoPixel:

    def __init__(self, _, count, auto_write):
        points = [ project( p ) for p in load_points() ]
        z_order = [ (p[2], p, i) for i, p in enumerate(points) ]
        z_order.sort()
        inf_order = [ i for _,_,i in z_order ]
        self.order = [None]*len(inf_order)
        for i,j in enumerate(inf_order):
            self.order[j] = i
        self.points = [ p[0:2] for _,p,_ in z_order ]
        self.disp = VirtualDisplay( self.points, (800,600) )
        self.pixels = [ [0,0,0] for _ in range(count) ]

        assert len(self.points) == count

    def show(self):
        self.disp.write(self.pixels)
        time.sleep(.03)

    def __getitem__(self, key):
        return self.pixels[self.order[key]]

    def __setitem__(self, key, value):
        self.pixels[self.order[key]] = value


