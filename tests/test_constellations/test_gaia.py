'''
Test basic constellation abilities.
'''

from thefriendlystars.imports import *
from thefriendlystars.constellations import *


label = 'gaia'
directory = 'examples'
mkdir(directory)

def test_cone():
    '''
    Can we do a cone query with Gaia?
    '''
    cone = Gaia('GJ1132')
    cone.finder()
    plt.savefig(os.path.join(directory, f'example-{label}-cone.pdf'))

def test_sky():
    '''
    Can we do sky-wide queries with Gaia?
    '''
    sky = Gaia(None, distancelimit=15)
    sky.allskyfinder()
    plt.savefig(os.path.join(directory, f'example-{label}-allsky.pdf'))

def test_motion():
    '''
    Will proper motions be animated correctly?
    '''
    sky = Gaia(None, distancelimit=15)
    sky.animate(os.path.join(directory, f'example-{label}-animation.mp4'), epochs=[0,10000], dt=500)
