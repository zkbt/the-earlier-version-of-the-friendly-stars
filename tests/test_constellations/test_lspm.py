'''
Test basic constellation abilities.
'''

from thefriendlystars.imports import *
from thefriendlystars.constellations import *

label = 'lspm'
directory = 'examples'
mkdir(directory)

def test_cone():
    cone = LSPM.from_cone('GJ1214', radius=1*u.deg)
    cone.finder()
    plt.savefig(os.path.join(directory, f'example-{label}-cone.pdf'))

def test_sky(magnitudelimit=10):
    sky = LSPM.from_sky(magnitudelimit=magnitudelimit)
    sky.allskyfinder()
    plt.savefig(os.path.join(directory,f'example-{label}-allsky.pdf'))

def test_motion(magnitudelimit=10):
    sky = LSPM.from_sky(magnitudelimit=magnitudelimit)
    sky.animate(os.path.join(directory, f'example-{label}-animation.mp4'), epochs=[0,10000], dt=500)

if __name__ == '__main__':
    # pull out anything that starts with `test_`
    d = locals()
    tests = [x for x in d if 'test_' in x]
    # run those functions and save their output
    outputs = {k.split('_')[-1]:d[k]()
               for k in tests}
