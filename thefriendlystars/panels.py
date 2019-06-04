
'''
Panel object contains
up to one image in the background,
and any number of catalogs plotted.
'''


from .imports import *
from .images import *
from .constellations import *



class Panel:
    '''
    A single frame of a finder chart.

    It can have up to one image in the background,
    and any number of catalogs over-plotted.
    '''
    def __init__(self, center, radius=3*u.arcmin,
                       image=None, constellations=None):

        self.image = image
        self.constellations = constellations
        pass
        #???
