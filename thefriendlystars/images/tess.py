from .astroqueryimages import *
from lightkurve import TessTargetPixelFile

class TESSImage(astroqueryImage):
    '''
    This is an image with a WCS, that's been cut from TESS FFIs.
    '''
    def __init__(self, center, radius=3*u.arcmin):

        # define the center
        self.center = center
        self.radius = radius
        self.survey = "TESS-FFI"

        # figure out the sectors
        sectors = Tesscut.get_sectors(self.center)

        # download the first sector
        tesshdulists = Tesscut.get_cutouts(self.center, self.radius, sector=sectors['sector'].data[0])

        # take just the first sector (ultimately, should make multiple!)
        self.hdulist = tesshdulists[0]
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
