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
                       constellations=[Gaia],
                       epoch=2020.0,
                       nickname=None):
        '''
        Initialize this finder chart with
        a center and a radius.
        '''

        Talker.__init__(self)

        # keep track of the center and radius of this finder
        self.center = center
        self.radius = radius

        self.speak(f'initializing a finder chart for {self}')

        # nudge to the requested epoch
        self.set_epoch(epoch)

        # populate all the necessary data in the panels
        self.setup_panels(images, constellations)

        self.nickname=nickname

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

        self.speak('populating finder chart panels')
        # create an empty list of panels
        self.panels = []

        # initialize all the constellations
        created_constellations = [create_constellation(c, self) # FIXME -- need that sqrt(2)!
                                                       #self.center,
                                                       #self.radius*np.sqrt(2))
                                    for c in constellations]

        # initialize all the images
        created_images = [create_image(i, self)
                                       #self.center,
                                       #self.radius)
                                    for i in images]

        # add panels to the finder
        for i in created_images:
            p = Panel(center=self,
                      image=i,
                      constellations=created_constellations)
            self.panels.append(p)
        self.speak(f'created {len(self.panels)} panels')

    def create_illustration(self):
        '''
        Plot a grid containing all the panels attached to this finder.
        '''

        # create all the illumination frames (one for each panel)
        #frames = self.panles



        self.illustration = GenericIllustration(imshows=self.panels,
                                           hspace=0.01,
                                           bottom=0.04,
                                           left=0.02, right=0.98,
                                           #shareimshowaxes=True,
                                           sharecolorbar=False)


        return self.illustration


    def draw_title(self, name=None):
        # define a name for this location
        if name is None:
            name = self.center

        if self.nickname is not None:
            name = f'{self.nickname} = {name}'

        # pull out a coordinate string for this object
        radec = self.center_skycoord.to_string("hmsdms",
                                               precision=1,
                                               alwayssign=False,
                                               pad=True,
                                               format='latex')

        # add an epoch, based on the coordinate center
        if self.center_skycoord.obstime is not None:
            epoch = f'{self.center_skycoord.obstime.decimalyear:.0f}'
        else:
            epoch = '????'

        title = f'{name} | {radec} ({epoch})'
        plt.suptitle(title, fontsize='xx-large')
        self.speak(f'added title to {self}')

    def plot(self, name=None, **kwargs):
        '''
        Plot a grid containing all the panels attached to this finder.
        '''

        # create the illustration and plot it
        self.create_illustration(**kwargs)
        self.illustration.plot()

        # add the title
        self.draw_title(name=name)

        # make sure the x + y limits are sent correctly
        r = self.radius.to('arcmin').value
        plt.xlim(r, -r)
        plt.ylim(-r, r)

        return self

    def savefig(self, filename=None, **kwargs):
        filename = filename or f'{self}.pdf'
        self.speak(f'saving finder chart to {filename}')
        plt.savefig(filename, **kwargs)

        return self
