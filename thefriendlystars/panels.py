
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
    def __init__(self, center,
                       radius=3*u.arcmin,
                       image=TwoMassJ,
                       constellations=[Gaia]):
        '''
        Parameters
        ----------
        image : None or thefriendlystars.images.image
            An image to display in the background of this panel.
        constellations : list of thefriendlystars.constellations.constellation
            A list of all the constellations to display in the
            foreground of this panel.
        '''

        # create the image (and the axes)
        self.image = create_image(image,
                                  center,
                                  radius=radius)

        # create the constellations to include
        self.constellations = [create_constellation(c,
                                                    center,
                                                    radius=radius)
                               for c in constellations]

    def plot(self, ax=None, gridspec=None):

        # plot the image, if there is one
        if self.image is not None:
            ax = self.image.imshow()

        # create axes if they don't already exist
        if ax is None:
            if gridspec is None:
                ax = plt.gca()
            else:
                ax = plt.subplot(gridspec)
        #else:
        #    ax.set_autoscale_on(False)

        # overplot all the stars
        for c in self.constellations:
            # try the epoch of the image; otherwise, the constellation's
            epoch = self.image.epoch or c.epoch
            c.atEpoch(epoch).plot(ax=ax, transform=self.image.transform, facecolor='none', edgecolor='black')
