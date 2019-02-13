
'''
Panel object contains
up to one image in the background,
and any number of catalogs plotted.
'''


from .imports import *
import astroquery.skyview


class Panel:
    '''
    A single frame of a finder chart,
    that has up to one image in the background,
    and any number of catalogs plotted.
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

        # replace this with an illumination frame?!
        inputs = dict(projection=self.wcs, sharex=share, sharey=share)
        if gridspec is None:
            ax = plt.subplot(**inputs)
        else:
            ax = plt.subplot(gridspec, **inputs)

        norm = plt.matplotlib.colors.SymLogNorm(
                              linthresh=mad_std(self.data),
                              linscale=0.1,
                              vmin=None,
                              vmax=None)
        ax.imshow(self.data, origin='lower', cmap='gray_r', norm=norm)
        transform = ax.get_transform('world')
        ax.set_title(self.survey)

        return ax



            #ax.grid(color='white', ls='solid')





class skyviewImage(Image):
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
        coordinatetosearch = '{0.ra.deg} {0.dec.deg}'.format(self.center)

        # query sky view for those images
        hdulist = astroquery.skyview.SkyView.get_images(
                                    position=coordinatetosearch,
                                    radius=self.radius,
                                    survey=self.survey)[0]

        return hdulist[0]



        # populate the images for each of these
        #self.images = [Image(p[0], s) for p, s in zip(paths, surveys)]
