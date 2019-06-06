'''
Images that can be accessed through astroquery.skyview
'''

from .image import *
import astroquery.skyview
from astroquery.mast import Tesscut
from urllib.request import HTTPError

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

        self.populate()
        self.guess_epoch()
        self.process_image()

    @property
    def filename(self):
        '''
        What's the default filename for this object?
        '''
        return f'{self}.pickled'

    def save(self):
        '''
        Save the hard-to-load data.
        '''
        with open(self.filename, 'wb') as file:
            pickle.dump(self._downloaded, file)

    def load(self):
        '''
        Load the hard-to-download data.
        '''
        with open(self.filename, 'rb') as file:
            self._downloaded = pickle.load(file)

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

        # simple access for the
        self.header = self._downloaded.header
        self.data = self._downloaded.data
        self.wcs = WCS(self._downloaded.header)

    def download(self):
        '''
        Do a search for the imaging data.
        (This relies on a .center and .radius
        having already been defined.)
        '''

        try:
            # query sky view for those images
            hdulist = astroquery.skyview.SkyView.get_images(
                                        position=self.center,
                                        radius=self.radius*np.sqrt(2),
                                        survey=self.survey)[0]
        except HTTPError:
            raise RuntimeError(f'''
                Uh-oh!

                It was hard to find
                {self.survey} image data
                centered on {self.center}
                with radius {self.radius}
                ''')
        self._downloaded = hdulist[0]

    def guess_epoch(self):
        '''
        Guess an approximate epoch for a skyview image.
        '''


        comments = self.header['COMMENT']

        self.epoch = None
        # one of the comment rows includes epoch
        for c in comments:
            if 'epoch' in c.lower():
                # often the epoch includes a range of years ("1997-2002")
                epochs = ''.join(c.split()[1:]).split('-')
                self.epoch = np.mean(np.array(epochs).astype(np.float))

    def process_image(self):
        pass





# define the images that accessible to skyview
#ukidss = ['UKIDSS-Y', 'UKIDSS-J', 'UKIDSS-H', 'UKIDSS-K']
