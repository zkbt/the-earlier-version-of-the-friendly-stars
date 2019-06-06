from .image import *
from .tess import *
from .dss import *
from .sdss import *
from .galex import *
from .twomass import *
from .wise import *

def create_image(image, *args, **kwargs):

    # is this a string?
    if type(image) == str:
        kwargs['survey'] = image
        return globals()[image](*args, **kwargs)

    # is the already an instance of a constellation?
    if isinstance(image, Image):
        return image

    # is this a class definition, which can be created?
    if issubclass(image, Image):
        return image(*args, **kwargs)



        # FIXME (change this to use a dictionary of objects?!)
