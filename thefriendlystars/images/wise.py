from .astroqueryimages import *

class W1(astroqueryImage):
    def __init__(self, *args, **kwargs):
        kwargs['survey'] = 'WISE 3.4'
        astroqueryImage.__init__(self, *args, **kwargs)


class W2(astroqueryImage):
    def __init__(self, *args, **kwargs):
        kwargs['survey'] = 'WISE 4.6'
        astroqueryImage.__init__(self, *args, **kwargs)


class W3(astroqueryImage):
    def __init__(self, *args, **kwargs):
        kwargs['survey'] = 'WISE 12'
        astroqueryImage.__init__(self, *args, **kwargs)

class W4(astroqueryImage):
    def __init__(self, *args, **kwargs):
        kwargs['survey'] = 'WISE 22'
        astroqueryImage.__init__(self, *args, **kwargs)
