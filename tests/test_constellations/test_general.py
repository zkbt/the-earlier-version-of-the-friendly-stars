'''
Test basic constellation abilities.
'''

from thefriendlystars.imports import *
from thefriendlystars.constellations import *

directory = 'examples'
mkdir(directory)

def test_epochs():
    '''
    Can we change the epoch of a constellation?
    '''
    cone = Gaia.from_cone('GJ1132')
    cone.finder()
    cone.atEpoch(2000).plot(color='red')
    plt.legend()
    plt.savefig(os.path.join(directory, 'gaia-cone-epochs.pdf'))

def test_cone():
    '''
    Can we do a cone query with Gaia?
    '''
    cone = Gaia.from_cone('GJ1132')
    cone.finder()
    plt.savefig(os.path.join(directory, 'example-gaia-cone.pdf'))

def test_gaiasky():
    '''
    Can we do sky-wide queries with Gaia?
    '''
    sky = Gaia.from_sky(distancelimit=15)
    sky.allskyfinder()
    plt.savefig(os.path.join(directory, 'example-gaia-allsky.pdf'))

def test_motion():
    '''
    Will proper motions be animated correctly?
    '''
    sky = Gaia.from_sky(distancelimit=15)
    sky.animate(os.path.join(directory, 'example-gaia-animation.mp4'), epochs=[0,10000], dt=500)

def test_custom(N=1000):
    '''
    Can we create a custom constellation of our own RA and Dec?
    '''

    ra = np.random.uniform(0, 360, N)*u.deg
    dec = np.random.uniform(-90,90, N)*u.deg
    mag = np.random.triangular(0, 20, 20, N)
    sky = Constellation.from_coordinates(ra=ra, dec=dec, mag=mag)
    sky.finder()
    plt.savefig(os.path.join(directory, 'example-custom.pdf'))
