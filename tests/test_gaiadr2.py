from thefriendlystars.constellations.gaia import *
from thefriendlystars.imports import *

directory = 'examples'
mkdir(directory)

def test_epochs():
    cone = Gaia.from_cone('GJ1132')
    cone.finder()
    cone.atEpoch(2000).plot(color='red')
    plt.legend()
    plt.savefig('examples/gaia-cone-epochs.pdf')

def test_cone():
    plt.savefig(os.path.join(directory, 'example-gaia-cone.pdf'))

def test_sky():
    sky = Gaia.from_sky(distancelimit=15)
    sky.allskyfinder()
    plt.savefig(os.path.join(directory, 'example-gaia-allsky.pdf'))

def test_motion():
    sky = Gaia.from_sky(distancelimit=15)
    sky.animate(os.path.join(directory, 'example-gaia-animation.mp4'), epochs=[0,10000], dt=500)
