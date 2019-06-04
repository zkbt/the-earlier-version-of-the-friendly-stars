from .astroqueryimages import *

class DSS(astroqueryImage):
    def process_image(self):
        self.data = self.data - np.median(self.data)


class DSS1b(DSS):
    def __init__(self, *args, **kwargs):
        kwargs['survey'] = 'DSS1 Blue'
        astroqueryImage.__init__(self, *args, **kwargs)

class DSS2b(DSS):
    def __init__(self, *args, **kwargs):
        kwargs['survey'] = 'DSS2 Blue'
        astroqueryImage.__init__(self, *args, **kwargs)

class DSS1r(DSS):
    def __init__(self, *args, **kwargs):
        kwargs['survey'] = 'DSS1 Red'
        astroqueryImage.__init__(self, *args, **kwargs)

class DSS2r(DSS):
    def __init__(self, *args, **kwargs):
        kwargs['survey'] = 'DSS2 Red'
        astroqueryImage.__init__(self, *args, **kwargs)
