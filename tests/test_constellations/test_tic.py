'''
Test basic constellation abilities.
'''

from thefriendlystars.imports import *
from thefriendlystars.constellations import *


label = 'tic'
directory = 'examples'
mkdir(directory)

def test_cone():
    '''
    Can we do a cone query with Gaia?
    '''
    cone = TIC('GJ1132')
    cone.finder()
    plt.savefig(os.path.join(directory, f'example-{label}-cone.pdf'))

def test_single():
    '''
    Can we query a single TIC?
    '''
    a = SingleTIC(101955023)
    b = SingleTIC('TIC101955023')
    c = SingleTIC('TIC 101955023')
    d = SingleTIC('tic101955023')
    e = SingleTIC('tic 101955023')


def test_motion():
    '''
    Will proper motions be animated correctly?
    '''
    sky = TIC('GJ1132')
    sky.animate(os.path.join(directory, f'example-{label}-animation.mp4'), epochs=[1900, 2100], dt=10)

if __name__ == '__main__':
    # pull out anything that starts with `test_`
    d = locals()
    tests = [x for x in d if 'test_' in x]
    # run those functions and save their output
    outputs = {k.split('_')[-1]:d[k]()
               for k in tests}
