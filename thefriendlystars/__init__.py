'''
The Friendly Stars (tfs) is a toolkit for managing catalogs of stars,
including tools for querying popular astronomy archives.
'''

from astropy.visualization import quantity_support
quantity_support()

from .imports import *
from .version import __version__

from .constellations import *
from .finders import *
from .panels import *
from . import io

def autosave_on():
    io.cache = True

def autosave_off():
    io.cache = False

def change_cache_directory(new):
    io.cache_directory = new
