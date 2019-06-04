'''
The Friendly Stars (tfs) is a toolkit for managing catalogs of stars,
including tools for querying popular astronomy archives.
'''

from astropy.visualization import quantity_support
quantity_support()

from .version import __version__
from .constellations import *
from .finders import *
from .panels import *
