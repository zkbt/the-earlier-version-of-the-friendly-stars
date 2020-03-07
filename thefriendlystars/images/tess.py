from .astroqueryimages import *
from lightkurve.search import search_tesscut
from lightkurve import TessTargetPixelFile
from .. import io

class TESS(astroqueryImage):
    '''
    This is an image with a WCS, that's been cut from TESS FFIs.
    '''


    def __init__(self, center,
                       radius=3*u.arcmin,
                       process='subtractbackground'):
        '''
        Initialize a sequence of images extracted from the TESS
        full frame images.

        Parameters
        ----------
        center : Field, str, SkyCoord
            Where's the center of the search?
        radius : astropy.units.quantity.Quantity
            How big of a radius to search?
        process : str
            Code indicating a process that should
            be applied to an image before displaying
        '''

        # define the center
        Field.__init__(self, center, radius)
        self.survey = "TESS-FFI"

        # keep track of any processes to apply
        self.process = process

        # populate the data
        self.populate()

        # try to figure out the epoch of the image
        self.guess_epoch()

        # apply any necessary processing to the image
        self.process_image()

    @property
    def filename(self):
        '''
        Create a fil
        '''

        return super().filename.replace('.pickled', '.fits')

    def save(self):
        '''
        Save the hard-to-load data (special for TESS TPF).
        '''
        if io.cache:
            mkdir(io.cache_directory)

            if self._downloaded is not None:
                with open(self.filename, 'wb') as file:
                        self._downloaded.to_fits(self.filename)
                        self.speak(f'saved file to {self.filename}')
            else:
                with open(self.filename, 'w') as file:
                        file.write('unavailable')
                        self.speak(f'saved a place-holder to {self.filename}')


    def load(self):
        '''
        Load the hard-to-download data (special for TESS TPF).
        '''
        self._downloaded = TessTargetPixelFile(self.filename)
        self.speak(f'loaded file from {self.filename}')


    def download(self):
        # figure out the sectors
        cutout_search = search_tesscut(self.center_skycoord)

        if len(cutout_search) > 0:
            # download only the first sector
            scale = 21*u.arcsec
            radius_in_pixels = np.ceil((self.radius/scale).decompose().value)
            cutout_size=int((2*radius_in_pixels + 1)*np.sqrt(2)) # overfill to get corners on a N-E square
            self.tpf = cutout_search.download(cutout_size=cutout_size)
        else:
            raise ImageUnavailableError(f"""
            TESS full-frame image data could not be
            found for '{self.center}', which has
            coordinates of {self.center_skycoord.to_string('hmsdms')}.
            """)
        self._downloaded = self.tpf

    def populate(self):
        '''
        Populate the data of this image.
        '''
        try:
            self.load()
            self.speak(f'loaded from {self.filename}')
        except (IOError, EOFError):
            self.speak(f'downloading data for {self}')
            self.download()
            self.save()

        if self._downloaded is None:
            raise ImageUnavailableError(f"""
            It's not clear exactly why, but somehow there
            is no image data defined for '{self.center}'.
            """)

        # take just the first sector (ultimately, should make multiple!)
        primary, pixels, aperture = self._downloaded.hdu

        # populate the header, data, WCS
        self.header = pixels.header
        self.data = np.median(pixels.data['FLUX'][:,:,:], 0) # KLUDGE?!
        self.wcs = WCS(aperture)

    def guess_epoch(self):
        '''
        Try to figure out the epoch of this image sequence,
        by taking the times directly from the TESS TPF.
        '''

        t_midpoint =  0.5*(self.header['TSTART'] + self.header['TSTOP'])
        bjd = self.header['BJDREFI'] + t_midpoint
        self.epoch = Time(bjd, format='jd').decimalyear
