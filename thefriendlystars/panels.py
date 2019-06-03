
'''
Panel object contains
up to one image in the background,
and any number of catalogs plotted.
'''


from .imports import *
import astroquery.skyview
from astroquery.mast import Tesscut
from lightkurve import TessTargetPixelFile


class Panel:
    '''
    A single frame of a finder chart.

    It can have up to one image in the background,
    and any number of catalogs over-plotted.
    '''
    def __init__(self, image, catalogs=None):
        pass
        #???

# define the images that accessible to skyview
twomass = ['2MASS-J', '2MASS-H', '2MASS-K']
ukidss = ['UKIDSS-Y', 'UKIDSS-J', 'UKIDSS-H', 'UKIDSS-K']
wise = ['WISE 3.4', 'WISE 4.6', 'WISE 12', 'WISE 22']
dss1 = ['DSS1 Blue', 'DSS1 Red']
dss2 = ['DSS2 Blue', 'DSS2 Red']
GALEX = ['GALEX Far UV', 'GALEX Near UV']

class Image:
    '''
    This represents images that lines up with a given patch of the sky.
    '''

    def __init__(self, hdu):
        '''
        Initialize an image.

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
        if gridspec is None:
            ax = plt.subplot(**inputs)
        else:
            ax = plt.subplot(gridspec, **inputs)

        # a quick normalization for the colors
        norm = plt.matplotlib.colors.SymLogNorm(
                              linthresh=mad_std(self.data),
                              linscale=0.1,
                              vmin=None,
                              vmax=None)
        # create the imshow
        ax.imshow(self.data, origin='lower', cmap='gray_r', norm=norm)
        transform = ax.get_transform('world')
        ax.set_title(self.survey)

        return ax


class astroqueryImage(Image):
    '''
    This is an image with a WCS, that's been downloaded from skyview.
    '''
    def __init__(self, center, radius=3*u.arcmin, survey='DSS1 Blue'):

        # store the search parameters
        self.center = center
        self.radius = radius
        self.survey = survey

        hdu = self.search()
        Image.__init__(self, hdu)

    def search(self):

        # what's the coordinate center?
        #coordinatetosearch = '{0.ra.deg} {0.dec.deg}'.format(self.center)

        # query sky view for those images
        hdulist = astroquery.skyview.SkyView.get_images(
                                    position=self.center,
                                    radius=self.radius,
                                    survey=self.survey)[0]

        return hdulist[0]


class TESSImage(astroqueryImage):
    def __init__(self, center, radius=3*u.arcmin):

        # define the center
        self.center = center
        self.radius=radius
        self.survey = "TESS-FFI"


        # figure out the sectors
        sectors = Tesscut.get_sectors(self.center)

        # download the first sector
        tesshdulists = Tesscut.get_cutouts(self.center, self.radius, sector=sectors['sector'].data[0])

        # take just the first sector (ultimately, should make multiple!)
        self.hdulist = tesshdulists[0]
        primary, pixels, aperture = self.hdulist

        self.header = pixels.header
        self.data = pixels.data['FLUX'][0]
        self.wcs = WCS(aperture)
