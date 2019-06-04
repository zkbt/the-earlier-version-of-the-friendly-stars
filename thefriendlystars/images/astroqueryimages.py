'''
Images that can be accessed through astroquery.skyview
'''

from .image import *
import astroquery.skyview
from astroquery.mast import Tesscut

class astroqueryImage(Image):
    '''
    This is an image with a WCS, that's been downloaded from skyview.
    '''
    def __init__(self, center,
                       radius=3*u.arcmin,
                       survey='DSS1 Blue'):

        # store the search parameters
        self.center = center
        self.radius = radius
        self.survey = survey

        hdu = self.search()
        Image.__init__(self, hdu)

    def search(self):
        '''
        Do a search for the imaging data.
        (This relies on a .center and .radius
        having already been defined.)
        '''

        # query sky view for those images
        hdulist = astroquery.skyview.SkyView.get_images(
                                    position=self.center,
                                    radius=self.radius,
                                    survey=self.survey)[0]

        return hdulist[0]

class TwoMassJ(astroqueryImage):
    def __init__(self, *args, **kwargs):
        kwargs['survey'] = '2MASS-J'
        astroqueryImage.__init__(self, *args, **kwargs)


class TwoMassH(astroqueryImage):
    def __init__(self, *args, **kwargs):
        kwargs['survey'] = '2MASS-H'
        astroqueryImage.__init__(self, *args, **kwargs)


class TwoMassK(astroqueryImage):
    def __init__(self, *args, **kwargs):
        kwargs['survey'] = '2MASS-K'
        astroqueryImage.__init__(self, *args, **kwargs)

class W1(astroqueryImage):
    def __init__(self, *args, **kwargs):
        kwargs['survey'] = 'WISE 3.4'
        astroqueryImage.__init__(self, *args, **kwargs)


class W2(astroqueryImage):
    def __init__(self, *args, **kwargs):
        kwargs['survey'] = 'WISE 4.6'
        astroqueryImage.__init__(self, *args, **kwargs)


class W3(astroqueryImage):
    def __init__(self, *args, **kwargs):
        kwargs['survey'] = 'WISE 12'
        astroqueryImage.__init__(self, *args, **kwargs)

class W4(astroqueryImage):
    def __init__(self, *args, **kwargs):
        kwargs['survey'] = 'WISE 22'
        astroqueryImage.__init__(self, *args, **kwargs)


class DSS1b(astroqueryImage):
    def __init__(self, *args, **kwargs):
        kwargs['survey'] = 'DSS1 Blue'
        astroqueryImage.__init__(self, *args, **kwargs)

class DSS2b(astroqueryImage):
    def __init__(self, *args, **kwargs):
        kwargs['survey'] = 'DSS2 Blue'
        astroqueryImage.__init__(self, *args, **kwargs)

class DSS1r(astroqueryImage):
    def __init__(self, *args, **kwargs):
        kwargs['survey'] = 'DSS1 Red'
        astroqueryImage.__init__(self, *args, **kwargs)

class DSS2r(astroqueryImage):
    def __init__(self, *args, **kwargs):
        kwargs['survey'] = 'DSS2 Red'
        astroqueryImage.__init__(self, *args, **kwargs)

class GALEXFUV(astroqueryImage):
    def __init__(self, *args, **kwargs):
        kwargs['survey'] = 'GALEX Far UV'
        astroqueryImage.__init__(self, *args, **kwargs)

class GALEXNUV(astroqueryImage):
    def __init__(self, *args, **kwargs):
        kwargs['survey'] = 'GALEX Near UV'
        astroqueryImage.__init__(self, *args, **kwargs)


class SDSSu(astroqueryImage):
    def __init__(self, *args, **kwargs):
        kwargs['survey'] = 'SDSSu'
        astroqueryImage.__init__(self, *args, **kwargs)

class SDSSg(astroqueryImage):
    def __init__(self, *args, **kwargs):
        kwargs['survey'] = 'SDSSg'
        astroqueryImage.__init__(self, *args, **kwargs)

class SDSSr(astroqueryImage):
    def __init__(self, *args, **kwargs):
        kwargs['survey'] = 'SDSSr'
        astroqueryImage.__init__(self, *args, **kwargs)

class SDSSi(astroqueryImage):
    def __init__(self, *args, **kwargs):
        kwargs['survey'] = 'SDSSi'
        astroqueryImage.__init__(self, *args, **kwargs)

class SDSSz(astroqueryImage):
    def __init__(self, *args, **kwargs):
        kwargs['survey'] = 'SDSSz'
        astroqueryImage.__init__(self, *args, **kwargs)
        # what's the difference with sdss DR7 on skyview?

# define the images that accessible to skyview
#ukidss = ['UKIDSS-Y', 'UKIDSS-J', 'UKIDSS-H', 'UKIDSS-K']
