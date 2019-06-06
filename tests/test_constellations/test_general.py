'''
Test basic constellation abilities.
'''

from thefriendlystars.imports import *
from thefriendlystars.constellations import *

directory = 'examples'
mkdir(directory)



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
