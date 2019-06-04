from .astroqueryimages import *


class SDSSu(astroqueryImage):
    def __init__(self, *args, **kwargs):
        kwargs['survey'] = 'SDSSu'
        astroqueryImage.__init__(self, *args, **kwargs)

class SDSSg(astroqueryImage):
    def __init__(self, *args, **kwargs):
        kwargs['survey'] = 'SDSSg'
        astroqueryImage.__init__(self, *args, **kwargs)

class SDSSr(astroqueryImage):
    def __init__(self, *args, **kwargs):
        kwargs['survey'] = 'SDSSr'
        astroqueryImage.__init__(self, *args, **kwargs)

class SDSSi(astroqueryImage):
    def __init__(self, *args, **kwargs):
        kwargs['survey'] = 'SDSSi'
        astroqueryImage.__init__(self, *args, **kwargs)

class SDSSz(astroqueryImage):
    def __init__(self, *args, **kwargs):
        kwargs['survey'] = 'SDSSz'
        astroqueryImage.__init__(self, *args, **kwargs)
        # what's the difference with sdss DR7 on skyview?
