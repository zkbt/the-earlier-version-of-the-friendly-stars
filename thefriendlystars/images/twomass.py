from .astroqueryimages import *

class TwoMass(astroqueryImage):
    def process_image(self):
        self.data = self.data - np.median(self.data)

class TwoMassJ(TwoMass):
    def __init__(self, *args, **kwargs):
        kwargs['survey'] = '2MASS-J'
        astroqueryImage.__init__(self, *args, **kwargs)


class TwoMassH(TwoMass):
    def __init__(self, *args, **kwargs):
        kwargs['survey'] = '2MASS-H'
        astroqueryImage.__init__(self, *args, **kwargs)


class TwoMassK(TwoMass):
    def __init__(self, *args, **kwargs):
        kwargs['survey'] = '2MASS-K'
        astroqueryImage.__init__(self, *args, **kwargs)
