'''
An empty Image to not break things when other images fail.
'''

from .image import *

class EmptyImage(Image):
    '''
    This is an image with a no data associated with it. It's here so
    that a Panel that finds no image data won't break.
    '''



    def __init__(self, center,
                       radius=3*u.arcmin,
                        **kwargs):

        # store the search parameters
        Field.__init__(self, center, radius)
        self.survey = 'empty'

        # simple access for the main ingredients
        self.header = None
        self.data = None
        self.wcs = None
        self.epoch = np.nan

        # make some dummy transforms
        self._pix2local = Affine2D.identity()
        self._local2pix = Affine2D.identity()

    def imshow(self, gridspec=None, share=None, transform=None):

        # this is where we will create the axes
        if gridspec is None:
            ax = plt.subplot(**inputs)
        else:
            ax = plt.subplot(gridspec, **inputs)

        plt.xlabel('(unavailable)')
