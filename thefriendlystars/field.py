from .imports import *

class Field(Talker):

    def __repr__(self):

        # what's the name of this survey?
        name = self.__class__.__name__

        # what's the target of this particular image
        if type(self.center) == str:
            target = self.center.replace(' ','')
        elif isinstance(self.center, coord.SkyCoord):
            target = self.center.to_string('hmsdms').replace(' ', '')

        # what's the radius out to which this image searched?
        size = self.radius.to('arcsec')

        return f'{name}-{target}-{size:.0f}'.replace(' ', '')
