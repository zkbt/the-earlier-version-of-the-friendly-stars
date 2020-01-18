
'''
Panel object contains
up to one image in the background,
and any number of catalogs plotted.
'''

from .imports import *
from .images import *
from .constellations import *
from illumination import imshowFrame

class Panel(Field, imshowFrame):
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
                       constellations=[Gaia],
                       plotingredients=['image', 'title', 'arrows'],
                       **kwargs):
        '''
        Parameters
        ----------
        center : str, SkyCoord
            The center of the field.
        radius : astropy.units.quantity.Quantity
            The radius out to which the field should stretch.
        image : None or thefriendlystars.images.image
            An image to display in the background of this panel.
            One or zero images are allowed.
        constellations : list of thefriendlystars.constellations.constellation
            A list of all the constellations to display in the
            foreground of this panel. Any number of constellations
            is allowed.
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


        #try:
            # create a frame, populated with this data
        imshowFrame.__init__(self,
                             data=self.image._downloaded, # FIXME; add a blank image?!
                             transform=self.image.pix2local,
                             plotingredients=plotingredients,
                             **kwargs)
        #except AttributeError:
        #    raise NotImplementedError('''
        #    As strange as it may seem, it hasn't yet been
        #    implemented to have a panel that doesn't have
        #    and image in it. Sorry!
        #    ''')

        # FIXME make this include the names of the constellations?!
        # change the title of the frame
        self.titlefordisplay = f'{self.image.survey} ({self.image.epoch:.0f})'



    def draw_arrows(self, origin=(-0.9, -0.9), ratio=0.2, alpha=0.5):
        '''
        Draw arrows on this Frame, to indicate the North and East directions.

        FIXME -- this could probably be tidied up with more careful use
        of transforms in the `draw_arrows` that comes with imshowFrame.

        Parameters
        ----------
        origin : tuple
            The (east, north) coordinates of the corner of the arrow,
            expressed as a fraction of the radius.
        ratio : float
            The size of the arrows,
            expressed as a fraction of the radius.
        '''


        r = self.radius.to('deg').value
        length = r*ratio
        origin = (r*origin[0], r*origin[1])

        # store the arrows in a dictionary
        arrows = {}

        # rotate into the display coordinates
        unrotatedx, unrotatedy = origin
        x, y = self._transformxy(*origin)
        arrow_kw = dict(zorder=10,  width=length * 0.06, head_width=length *
                        0.3, head_length=length * 0.2, clip_on=False, length_includes_head=True,
                        alpha=alpha, edgecolor='none', facecolor='black')
        text_kw = dict(color='black',
                       fontsize=7, fontweight='bold', clip_on=False, alpha=alpha)
        buffer = 1.1

        # +x arrow
        dx, dy = np.asarray(self._transformxy(unrotatedx + length, unrotatedy)) - \
            np.asarray(self._transformxy(unrotatedx, unrotatedy))
        arrows['xarrow'] = self.ax.arrow(x, y, dx, dy, **arrow_kw)
        xtextx, xtexty = self._transformxy(
            unrotatedx + length * buffer, unrotatedy)
        arrows['xarrowlabel'] = self.ax.text(xtextx, xtexty, 'E', ha='right', va='center', **text_kw)

        # +y arrow
        dx, dy = np.asarray(self._transformxy(unrotatedx, unrotatedy + length)) - \
            np.asarray(self._transformxy(unrotatedx, unrotatedy))
        arrows['yarrow'] = self.ax.arrow(x, y, dx, dy, **arrow_kw)
        ytextx, ytexty = self._transformxy(
            unrotatedx, unrotatedy + length * buffer)
        arrows['yarrowlabel'] = self.ax.text(ytextx, ytexty, 'N', ha='center', va='bottom', **text_kw)

        return arrows

    def plot(self, *args, **kwargs):
        '''
        Plot this panel, including an image and/or
        some constellations, in local tangent plane
        coordinates. The center of the field is
        at (0, 0), and the scale is in angles on sky.
        '''

        # kludge?
        imshowFrame.plot(self, *args, **kwargs)

        
        # overplot all the constellations as stars
        plt.sca(self.ax)
        for c in self.constellations:
            # try the epoch of the image; otherwise, the constellation's
            epoch = self.image.epoch or c.epoch
            now = c.at_epoch(epoch)
            now.plot(ax=self.ax, facecolor='none', edgecolor='black')
