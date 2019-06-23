
'''
Panel object contains
up to one image in the background,
and any number of catalogs plotted.
'''


from .imports import *
from .images import *
from .constellations import *


class Panel(Field):
    '''
    A single frame of a finder chart.

    It can have up to one image in the background,
    and any number of catalogs over-plotted.
    '''
    def __repr__(self):
        '''
        How should this panel be represented as a string?
        '''
        listofcon = '+'.join([repr(c).split('-')[0] for c in self.constellations])
        return f'{listofcon}|{self.image}'

    def __init__(self, center,
                       radius=3*u.arcmin,
                       image=TwoMassJ,
                       constellations=[Gaia]):
        '''
        Parameters
        ----------
        center : str, SkyCoord
            The center of the field.
        radius : astropy.units.quantity.Quantity
            The radius out to which the field should stretch.
        image : None or thefriendlystars.images.image
            An image to display in the background of this panel.
        constellations : list of thefriendlystars.constellations.constellation
            A list of all the constellations to display in the
            foreground of this panel.
        '''

        # the center of this field
        self.center = center
        self.radius = radius

        # create the image (and the axes)
        self.image = create_image(image,
                                  center,
                                  radius=radius)

        # create the constellations to include
        self.constellations = [create_constellation(c,
                                                    center,
                                                    radius=radius)
                               for c in constellations]

    def create_frame(self, **kwargs):
        '''
        Create an `illumination` frame into which this panel can be plotted.
        '''
        try:
            return self.image.create_frame(**kwargs)
        except AttributeError:
            raise NotImplementedError('''
            As strange as it may seem, it hasn't yet been
            implemented to have a panel that doesn't have
            and image in it. Sorry!
            ''')

    def plot(self, ax=None, gridspec=None, share=None):
        '''
        Plot this panel, including an image and/or
        some constellations, in local tangent plane
        coordinates. The center of the field is
        at (0, 0), and the scale is in angles on sky.

        Parameters
        ----------
        ax : matplotlib.axes._subplots.AxesSubplot
            The axes into which this image should be plotted.
        gridspec : matplotlib.gridspec.SubplotSpec
            The gridspec specification into which this
            image should be plotted.
        share : matplotlib.axes._subplots.AxesSubplot
            The axes with which this panel should share
            its x and y limits.

        Returns
        -------
        ax : matplotlib.axes._subplots.AxesSubplot
            The axes into which this panel was plotted.
        '''

        # plot the image, if there is one
        if self.image is not None:
            ax = self.image.imshow(gridspec=gridspec, share=share)

        # create axes if they don't already exist
        if ax is None:
            if gridspec is None:
                ax = plt.gca()
            else:
                ax = plt.subplot(gridspec)

        # overplot all the constellations as stars
        for c in self.constellations:
            # try the epoch of the image; otherwise, the constellation's
            epoch = self.image.epoch or c.epoch
            now = c.at_epoch(epoch)
            now.plot(ax=ax, facecolor='none', edgecolor='black')

        # return the axes, for ease of connecting with others
        return ax
