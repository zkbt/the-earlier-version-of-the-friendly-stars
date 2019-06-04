
'''
Panel object contains
up to one image in the background,
and any number of catalogs plotted.
'''


from ..imports import *

class Image:
    '''
    This represents images that lines up
    with a given patch of the sky.
    '''

    def __init__(self, hdu):
        '''
        Initialize an image.

        (This will likely be overwritten
        by classes that inherit from Image.)

        Parameters
        ----------

        hdu : a single FITS extension
            This HDU should contain both an image to display
            and a good WCS that goes along with it.
        '''

        # simple access for the
        self.header = hdu.header
        self.data = hdu.data
        self.wcs = WCS(hdu.header)

    def imshow(self, gridspec=None, share=None):
        '''
        Plot this image as an imshow.

        Parameters
        ----------
        gridspec : matplotlib.gridspec.SubplotSpec
            Should this image go into an existing spot?
        share : matplotlib.axes._subplots.AxesSubplot
            Should this imshow share the same axes
            limits as another existing axes?
        '''


        # replace this with an illumination frame?!
        inputs = dict(projection=self.wcs, sharex=share, sharey=share)

        # this is where we will create the axes
        if gridspec is None:
            ax = plt.subplot(**inputs)
        else:
            ax = plt.subplot(gridspec, **inputs)

        # a quick normalization for the colors
        norm = plt.matplotlib.colors.SymLogNorm(
                              linthresh=mad_std(self.data),
                              linscale=1,
                              vmin=-np.max(self.data),
                              vmax=np.max(self.data))

        # create the imshow
        ax.imshow(self.data, origin='lower', cmap='RdBu', norm=norm)

        # store the axes transform
        self.transform = ax.get_transform('icrs')

        # set the title of the axes
        ax.set_title(f'{self.survey} ({self.epoch:.0f})')

        self.ax = ax
        return ax

class NoImage:
    def __init__(self, *args, **kwargs):
        self.header = None
        self.data = None
        self.wcs = None
        self.epoch = None
        self.transform = None

    def imshow(self, *args, **kwargs):
        pass
