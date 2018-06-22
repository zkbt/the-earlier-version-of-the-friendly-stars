
'''
Panel object contains
up to one image in the background,
and any number of catalogs plotted.
'''

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

    def __init__(self, hdu, name=None):
        '''
        Initialize an image.

        Parameters
        ----------

        hdu : a PrimaryHDU file
            FITS file
        '''

        self.header = hdu.header
        self.data = hdu.data
        self.wcs = WCS(hdu.header)
        self.name = name
