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







        # figure out an approximate epoch for this image
        self.populate()
        self.guess_epoch()
        self.process_image()

    def download(self):
        # figure out the sectors
        cutout_search = search_tesscut(self.center)

        # download only the first sector
        scale = 21*u.arcsec
        radius_in_pixels = np.ceil((self.radius/scale).decompose().value)
        self.tpf = cutout_search.download(cutout_size=2*radius_in_pixels + 1)
        self._downloaded = self.tpf



    def populate(self):
        '''
        Populate the data of this image.
        '''
        try:
            self.load()
            print(f'loaded from {self.filename}')
        except IOError:
            print(f'using astroquery to initialize {self}')
            self.download()
            self.save()

        # take just the first sector (ultimately, should make multiple!)
        primary, pixels, aperture = self._downloaded.hdu

        # populate the header, data, WCS
        self.header = pixels.header
        self.data = pixels.data['FLUX'][0]
        self.wcs = WCS(aperture)

    def guess_epoch(self):
        bjd = self.header['BJDREFI'] + 0.5*(self.header['TSTART'] + self.header['TSTOP'])
        self.epoch = Time(bjd, format='jd').decimalyear

    def process_image(self):
        self.data = self.data - np.median(self.data)
