from .astroqueryimages import *
from lightkurve.search import search_tesscut

class TESS(astroqueryImage):
    '''
    This is an image with a WCS, that's been cut from TESS FFIs.
    '''
    def __init__(self, center, radius=3*u.arcmin):

        # define the center
        self.center = center
        self.radius = radius
        self.survey = "TESS-FFI"

        # figure out the sectors
        cutout_search = search_tesscut(self.center)

        # download only the first sector
        self.tpf = cutout_search.download()

        # take just the first sector (ultimately, should make multiple!)
        self.hdulist = self.tpf.hdu
        primary, pixels, aperture = self.hdulist


        # populate the header, data, WCS
        self.header = pixels.header
        self.data = pixels.data['FLUX'][0]
        self.wcs = WCS(aperture)


        # figure out an approximate epoch for this image
        bjd = self.header['BJDREFI'] + 0.5*(self.header['TSTART'] + self.header['TSTOP'])
        self.epoch = Time(bjd, format='jd').decimalyear

        self.process_image()

    def process_image(self):
        self.data = self.data - np.median(self.data)
