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
                       survey='DSS1 Blue',
                       process='subtractbackground'):

        # store the search parameters
        Field.__init__(self, center, radius)
        self.survey = survey

        self.populate()

        # simple access for the main ingredients
        self.header = self._downloaded.header
        self.data = self._downloaded.data
        self.wcs = WCS(self._downloaded.header)

        self.process = process
        self.guess_epoch()
        self.process_image()



    def download(self):
        '''
        Do a search for the imaging data.
        (This relies on a .center and .radius
        having already been defined.)
        '''

        try:
            # query sky view for those images
            hdulist = astroquery.skyview.SkyView.get_images(
                                        position=self.coordinate_center,
                                        radius=self.radius*2,
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
        if self.process == 'subtractbackground':
            self.data -= np.median(self.data)





# define the images that accessible to skyview
#ukidss = ['UKIDSS-Y', 'UKIDSS-J', 'UKIDSS-H', 'UKIDSS-K']
