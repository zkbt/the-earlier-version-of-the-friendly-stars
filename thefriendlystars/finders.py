'''
Finder object contains one or more Panels,
each with its own image and catalogs.
The Finder object makes sure all the data
get collected and manages the organization
and visualization.
'''

from .imports import *
from .panels import *
from .images import *
from .constellations import *


# define som
class Finder(Talker):
    '''
    A Finder object creates a finder chart,
    containing one or more panels. It's centered
    on a particular location.
    '''

    def __init__(self, center,
                       radius=3*u.arcmin,
                       images=[DSS2r, TwoMassJ, TESS],
                       constellations=[Gaia]):
        '''
        Initialize this finder chart with
        a center and a radius.
        '''
        self.center = center
        self.radius = radius
        self.setup_panels(images, constellations)

    def setup_panels(self, images=[], constellations=[]):

        self.panels = []
        # initialize all the constellations
        created_constellations = [create_constellation(c,
                                                       self.center,
                                                       self.radius)
                                    for c in tqdm(constellations)]

        # initialize all the images
        created_images = [create_image(i,
                                       self.center,
                                       self.radius)
                                    for i in tqdm(images)]

        # add panels to the finder
        for i in created_images:
            p = Panel(center=self.center,
                      radius=self.radius,
                      image=i,
                      constellations=created_constellations)

            self.panels.append(p)

    def plot_grid(self):

        N = len(self.panels)
        fig = plt.figure(figsize=(N*3, 3), dpi=200)
        gs = plt.matplotlib.gridspec.GridSpec(1, N)

        self.ax = {}
        share = None
        for i, panel in enumerate(self.panels):
            share = panel.plot(gridspec=gs[i])
