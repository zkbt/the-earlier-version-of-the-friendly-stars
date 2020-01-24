from .astroqueryimages import *
from lightkurve.search import search_tesscut
from lightkurve import TessTargetPixelFile
from .. import io

class TESS(astroqueryImage):
    '''
    This is an image with a WCS, that's been cut from TESS FFIs.
    '''


    def __init__(self, center, radius=3*u.arcmin, process='subtractbackground'):

        # define the center
        Field.__init__(self, center, radius)
        self.survey = "TESS-FFI"


        self.process = process
        # figure out an approximate epoch for this image
        self.populate()
        self.guess_epoch()
        self.process_image()

    @property
    def filename(self):
        return super().filename.replace('.pickled', '.fits')

    def save(self):
        '''
        Save the hard-to-load data (special for TESS TPF).
        '''
        if io.cache:
            mkdir(io.cache_directory)

            with open(self.filename, 'wb') as file:
                self._downloaded.to_fits(self.filename)
                print(f'saved file to {self.filename}')

    def load(self):
        '''
        Load the hard-to-download data (special for TESS TPF).
        '''
        self._downloaded = TessTargetPixelFile(self.filename)
        print(f'loaded file from {self.filename}')


    def download(self):
        # figure out the sectors
        cutout_search = search_tesscut(self.coordinate_center)

        # download only the first sector
        scale = 21*u.arcsec
        radius_in_pixels = np.ceil((self.radius/scale).decompose().value)
        cutout_size=int((2*radius_in_pixels + 1)*np.sqrt(2)) # overfill to get corners on a N-E square
        self.tpf = cutout_search.download(cutout_size=cutout_size)
        self._downloaded = self.tpf

    def populate(self):
        '''
        Populate the data of this image.
        '''
        try:
            self.load()
            print(f'loaded from {self.filename}')
        except (IOError, EOFError):
            print(f'downloading data for {self}')
            self.download()
            self.save()

        # take just the first sector (ultimately, should make multiple!)
        primary, pixels, aperture = self._downloaded.hdu

        # populate the header, data, WCS
        self.header = pixels.header
        self.data = np.median(pixels.data['FLUX'][:,:,:], 0) # KLUDGE?!
        self.wcs = WCS(aperture)

    def guess_epoch(self):
        bjd = self.header['BJDREFI'] + 0.5*(self.header['TSTART'] + self.header['TSTOP'])
        self.epoch = Time(bjd, format='jd').decimalyear

    #def process_image(self):
    #    self.data = self.data - np.median(self.data)
