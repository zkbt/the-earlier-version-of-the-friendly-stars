from .astroqueryimages import *

class GALEXFUV(astroqueryImage):
    def __init__(self, *args, **kwargs):
        kwargs['survey'] = 'GALEX Far UV'
        astroqueryImage.__init__(self, *args, **kwargs)

class GALEXNUV(astroqueryImage):
    def __init__(self, *args, **kwargs):
        kwargs['survey'] = 'GALEX Near UV'
        astroqueryImage.__init__(self, *args, **kwargs)
