# basic tools
import matplotlib.pyplot as plt
import matplotlib.animation as ani
import numpy as np
import warnings, os, copy, glob
from tqdm import tqdm

# some standard astropy tools
import astropy.units as u, astropy.coordinates as coord
from astropy.io import fits, ascii
from astropy.wcs import WCS
from astropy.time import Time
from astropy.table import Table, QTable
from astropy.stats import mad_std

import pickle

# a handy tool for speaking classes
from .talker import Talker

def mkdir(path):
        '''
        A mkdir that doesn't complain if it already exists.
        '''
        try:
            os.mkdir(path)
            print("made {}".format(path))
        except:
            pass

def filename(name, target, radius):

    # what's the target of this particular image
    if type(center) == str:
        target = center.replace(' ','')
    elif isinstance(center, coord.SkyCoord):
        target = center.to_string('hmsdms').replace(' ', '')

    # what's the radius out to which this image searched?
    size = radius.to('arcsec')

    return f'{name}-{target}-{size:.0f}.pickled'.replace(' ', '')
