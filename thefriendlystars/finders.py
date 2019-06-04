'''
Finder object contains one or more Panels,
each with its own image and catalogs.
The Finder object makes sure all the data
get collected and manages the organization
and visualization.
'''

from .imports import *
from .panels import *
from .constellations import *


# define som
class Finder(Talker):
    '''
    A Finder object creates a finder chart,
    containing one or more panels. It's centered
    on a particular location.
    '''

    def __init__(self, center, radius=3*u.arcmin):
        '''
        Initialize this finder chart with
        a center and a radius.
        '''
        self.center = parse_center(center)
        self.radius = radius

    def populateImagesFromSurveys(self, surveys=[]):
        '''
        Load images from archives.
        '''
        self.images = [astroqueryImage(self.center, self.radius, s) for s in surveys]

    def populateCatalogsFromSurveys(self, surveys=[Gaia, TwoMass, GALEX, TIC]):

        self.catalogs = {}
        for s in surveys:
            this = s(self.center, self.radius)
            self.catalogs[this.name] = this

    def plotGrid(self):

        N = len(self.images)
        fig = plt.figure(figsize=(3, N), dpi=200)
        gs = plt.matplotlib.gridspec.GridSpec(1, N)

        self.ax = {}
        share = None
        for i, image in enumerate(self.images):
            share = image.imshow(gs[i])
            self.ax[image.survey] = share
