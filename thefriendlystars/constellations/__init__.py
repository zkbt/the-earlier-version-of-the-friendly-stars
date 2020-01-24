from .constellation import *
from .gaia import *
#from .lspm import *
#from .others import *
from .tic import *

def create_constellation(constellation, *args, **kwargs):

    # is this a string?
    if type(constellation) == str:
        return globals()[constellation](*args, **kwargs)

    # is the already an instance of a constellation?
    if isinstance(constellation, Constellation):
        return constellation

    # is this a class definition, which can be created?
    if issubclass(constellation, Constellation):
        return constellation(*args, **kwargs)
