
'''
Panel object contains
up to one image in the background,
and any number of catalogs plotted.
'''

from .imports import *
from .images import *
from .constellations import *
from illumination import imshowFrame


unit = 'arcmin'


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
        return f'<{listofcon}|{self.image}>'

    def __init__(self, center,
                       radius=3*u.arcmin,
                       image=TwoMassJ,
                       constellations=[Gaia],
                       plotingredients=['image',
                                        'title',
                                        'compass',
                                        'ruler',
                                        'crosshair'],
                       unit=u.arcmin,
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
        plotingredients : list
            The components that should be included when plotting.
            These include:
                image = the actual imshow of the image
                title = a title over the top of the frame
                arrows = arrows indicating the N + E directions
                axes = lines, ticks, labels around the axes
                ruler = scale bar showing the scale of the image
        unit : astropy.units.core.Unit
            The default units with which any plots will be made.

        '''


        # the center of this field
        Field.__init__(self, center, radius)

        # create the image (and the axes)
        self.image = create_image(image, self)

        # create the constellations to include
        self.constellations = [create_constellation(c, self)
                               for c in constellations]


        # create a frame, populated with this data
        imshowFrame.__init__(self,
                             data=self.image.data, # FIXME; add a blank image?!
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

    def draw_compass(self, origin=(-1, -1), ratio=0.3, alpha=0.5):
        '''
        Draw arrows on this Frame, to indicate the North and East directions.


        Parameters
        ----------
        origin : tuple
            The (east, north) coordinates of the corner of the arrow,
            expressed as a fraction of half the side of the square.
        ratio : float
            The size of the arrows,
            expressed as a fraction of half the side of the square.
        '''


        # define the location and size of the arrows
        L = self.radius.to('arcmin').value
        length = L*ratio
        origin = (L*origin[0], L*origin[1])

        # store the arrows in a dictionary
        arrows = {}

        # rotate into the display coordinates
        unrotatedx, unrotatedy = origin
        x, y = self._transformxy(*origin)
        arrow_kw = dict(zorder=10,  width=length * 0.08, head_width=length *
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
        arrows['xarrowlabel'] = self.ax.text(xtextx, xtexty, 'E',
                                    ha='right', va='center', **text_kw)

        # +y arrow
        dx, dy = np.asarray(self._transformxy(unrotatedx, unrotatedy + length)) - \
            np.asarray(self._transformxy(unrotatedx, unrotatedy))
        arrows['yarrow'] = self.ax.arrow(x, y, dx, dy, **arrow_kw)
        ytextx, ytexty = self._transformxy(
            unrotatedx, unrotatedy + length * buffer)
        arrows['yarrowlabel'] = self.ax.text(ytextx, ytexty, 'N',
                                    ha='center', va='bottom', **text_kw)

        return arrows

    def draw_circle(self, origin=(0.0, 0.0), ratio=1, round=False, alpha=0.5):
        '''
        Draw circle on this frame, to indicate the scale of the image.

        FIXME -- this could probably be tidied up with more careful use
        of transforms in the `draw_arrows` that comes with imshowFrame.

        Parameters
        ----------
        origin : tuple
            The (east, north) coordinates of the center of the ruler,
            expressed as a fraction of half the side of the square.
        ratio : float
            The approximate desired size of the ruler,
            expressed as a fraction of half the side of the square.
        round : bool
            Should the size of the ruler be rounded to an integer?
        '''



        # define the location and size of the arrows
        L = self.radius.to(unit).value
        desired_length = L*ratio

        circle_radius = np.maximum(np.round(desired_length), 1)
        x_center, y_center = 0, 0

        # store the arrows in a dictionary
        ruler = {}

        # plot the line
        linekw = dict(zorder=10, linewidth=2, linestyle='--', clip_on=False, alpha=alpha,
                        color='black')

        N = 1000
        theta = np.linspace(0, 2*np.pi, N)
        r = circle_radius*np.ones_like(theta)

        ruler['circleline'] = plt.plot(r*np.cos(theta), r*np.sin(theta), **linekw)

        # add the label
        text_kw = dict(color='black',
                       fontsize=7, fontweight='bold', clip_on=False, alpha=alpha)

        ruler['circlelabel'] = self.ax.text(x_center + circle_radius/np.sqrt(2)*1.05,
                                            y_center - circle_radius/np.sqrt(2)*1.05,
                                    f"{circle_radius}' radius",
                                    ha='center', va='center',
                                    rotation=-45,
                                    **text_kw)



        return ruler


    def draw_ruler(self, origin=(0.0, -1), ratio=0.2, round=True, alpha=1):
        '''
        Draw ruler on this frame, to indicate the scale of the image.

        FIXME -- this could probably be tidied up with more careful use
        of transforms in the `draw_arrows` that comes with imshowFrame.

        Parameters
        ----------
        origin : tuple
            The (east, north) coordinates of the center of the ruler,
            expressed as a fraction of half the side of the square.
        ratio : float
            The approximate desired size of the ruler,
            expressed as a fraction of half the side of the square.
        round : bool
            Should the size of the ruler be rounded to an integer?
        '''




        # define the location and size of the arrows
        L = self.radius.to(unit).value
        desired_length = L*ratio

        length = np.maximum(np.round(desired_length), 1)
        x_center, y_center = (L*origin[0], L*origin[1])


        # store the arrows in a dictionary
        ruler = {}

        # plot the line
        linekw = dict(zorder=10, linewidth=4, clip_on=False, alpha=alpha,
                        color='black')
        ruler['rulerline'] = plt.plot([x_center - length/2,
                                        x_center + length/2],
                                       [y_center, y_center],
                                       **linekw)

        # add the label
        text_kw = dict(color='black',
                       fontsize=7, fontweight='bold', clip_on=False, alpha=alpha)

        ruler['rulerlabel'] = self.ax.text(x_center, y_center,
                                    f"\n{length}'",
                                    ha='center', va='top',
                                    **text_kw)



        return ruler


    def draw_crosshair(self, ratio=0.2, alpha=0.5):
        '''
        Draw a crosshair pointing at the center of this frame.

        FIXME -- this could probably be tidied up with more careful use
        of transforms in the `draw_arrows` that comes with imshowFrame.

        Parameters
        ----------

        ratio : float
            The approximate desired size of the cross hair marks,
            expressed as a fraction of half the side of the square.
        '''

        # define the location and size of the arrows
        L = self.radius.to(unit).value
        s = L*ratio

        # store the arrows in a dictionary
        ruler = {}

        # plot the line
        linekw = dict(zorder=10, linewidth=2, clip_on=False, alpha=alpha,
                        color='black')

        ruler['crosshairtop'] = plt.plot([0,0], [s*0.5, s*1.5], **linekw)
        ruler['crosshairbottom'] = plt.plot([0,0], [-s*0.5, -s*1.5], **linekw)
        ruler['crosshairright'] = plt.plot([-s*0.5, -s*1.5], [0,0], **linekw)
        ruler['crosshairleft'] = plt.plot([s*0.5, s*1.5], [0,0], **linekw)

        return ruler


    def plot(self, *args, **kwargs):
        '''
        Plot this panel, including an image and/or
        some constellations, in local tangent plane
        coordinates. The center of the field is
        at (0, 0), and the scale is in angles on sky.
        '''

        # plot the image of this frame (using illumination)
        if isinstance(self.image, EmptyImage) == False:
            imshowFrame.plot(self, *args, **kwargs)

        # overplot all the constellations as stars
        plt.sca(self.ax)
        for c in self.constellations:
            # try the epoch of the image; otherwise, the constellation's
            epoch = self.image.epoch or c.epoch
            # create a catalog of position at that epoch
            now = c.at_epoch(epoch)
            # plot the stellar positions into the frame
            now.plot(ax=self.ax, facecolor='none', edgecolor='black',
                    celestial2local=self.celestial2local)

        if 'axes' in self.plotingredients:
            plt.xlabel(f'$\Delta$RA ({self.ax.xaxis.units})')
            plt.ylabel(f'$\Delta$Dec ({self.ax.xaxis.units})')

        if 'ruler' in self.plotingredients:
            #self.draw_ruler()
            self.draw_circle()
        if 'compass' in self.plotingredients:
            self.draw_compass()

        if 'crosshair' in self.plotingredients:
            self.draw_crosshair()

        # make sure the axes get flipped
        R = self.radius
        plt.xlim(R, -R)
        plt.ylim(-R, R)
