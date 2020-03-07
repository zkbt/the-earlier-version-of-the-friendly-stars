# basic tools
import matplotlib.pyplot as plt
import matplotlib.animation as ani
import numpy as np
import warnings, os, copy, glob
import pytest
from tqdm import tqdm

# some standard astropy tools
import astropy.units as u
from astropy.coordinates import SkyCoord
from astropy.coordinates.name_resolve import NameResolveError

import astropy.io.fits
astropy.io.fits.conf.use_memmap = False
from astropy.io import fits, ascii
from astropy.wcs import WCS
from astropy.time import Time
from astropy.table import Table, QTable, hstack

from astropy.stats import mad_std
from matplotlib.transforms import Affine2D



from astropy.utils.exceptions import ErfaWarning
warnings.simplefilter('ignore', ErfaWarning)

import pickle

# a handy tool for speaking classes
from illumination.talker import Talker

def mkdir(path):
        '''
        A mkdir that doesn't complain if it already exists.
        '''
        try:
            os.mkdir(path)
            print("made the directory {}".format(path))
        except:
            pass


def convert_epoch_to_time(epoch):
    '''
    Make sure an epoch gets converted into an astropy time.
    '''
    if type(epoch) == Time:
        t = epoch
    elif type(epoch) == u.Quantity:
        t = Time(epoch.to('year').value, format='decimalyear')
    elif type(epoch) == str:
        t = Time(epoch)
    else:
        t = Time(epoch, format='decimalyear')
    assert(type(t) == Time)
    return t

def convert_time_to_epoch(time):
    '''
    Convert an astropy time to a simple epoch number.
    '''
    return time.decimalyear
