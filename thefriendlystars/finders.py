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
from illumination import GenericIllustration

# define som
class Finder(Field):
    '''
    A Finder object creates a finder chart,
    containing one or more panels. It's centered
    on a particular location.
    '''

    def __init__(self, center,
                       radius=5*u.arcmin,
                       images=[DSS2r, TwoMassJ, TESS],
                       constellations=[Gaia]):
        '''
        Initialize this finder chart with
        a center and a radius.
        '''

        # keep track of the center and radius of this finder
        self.center = center
        self.radius = radius

        # populate all the necessary data in the panels
        self.setup_panels(images, constellations)

    def setup_panels(self, images=[], constellations=[]):
        '''
        Populate the panels that will go into this finder.

        Parameters
        ----------
        images : list
            A list of all the images to include. Right now,
            each image by default gets *its own* panel.
        constellations : list
            A list of all the constellations to include. Right now,
            each constellation will be plotted in *every* panel.
        '''

        # create an empty list of panels
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

    def create_illustration(self, plotingredients=['image', 'colorbar', 'axes']):
        '''
        Plot a grid containing all the panels attached to this finder.
        '''

        # create all the illumination frames (one for each panel)
        #frames = self.panles



        illustration = GenericIllustration(imshows=self.panels,
                                           #shareimshowaxes=True,
                                           sharecolorbar=False)


        return illustration



    def plot(self, **kwargs):
        '''
        Plot a grid containing all the panels attached to this finder.
        '''

        illustration = self.create_illustration(**kwargs)
        illustration.plot()

        #r = self.radius.to('deg').value
        #plt.xlim(r, -r) # put East on the left
        #plt.ylim(-r, r)

        return illustration
