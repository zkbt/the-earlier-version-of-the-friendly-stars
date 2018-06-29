from thefriendlystars.constellations.lspm import *

directory = 'examples'
mkdir(directory)

def test_cone():
    cone = LSPM.from_cone('GJ1214', radius=1*u.deg)
    cone.finder()
    plt.savefig(os.path.join(directory, 'example-lspm-cone.pdf'))

def test_sky(magnitudelimit=10):
    sky = LSPM.from_sky(magnitudelimit=magnitudelimit)
    sky.allskyfinder()
    plt.savefig(os.path.join(directory,'example-lspm-allsky.pdf'))

def test_motion(magnitudelimit=10):
    sky = LSPM.from_sky(magnitudelimit=magnitudelimit)
    sky.animate(os.path.join(directory, 'example-lspm-animation.mp4'), epochs=[0,10000], dt=500)
