from thefriendlystars.constellations.lspm import *

def test_cone():
    cone = LSPM.from_cone('GJ1214', radius=1*u.deg)
    cone.finder()
    plt.savefig('example-lspm-cone.pdf')

def test_sky(magnitudelimit=10):
    sky = LSPM.from_sky(magnitudelimit=magnitudelimit)
    sky.allskyfinder()
    plt.savefig('example-lspm-allsky.pdf')

def test_motion(magnitudelimit=10):
    sky = LSPM.from_sky(magnitudelimit=magnitudelimit)
    sky.animate('example-lspm-animation.mp4', epochs=[0,10000], dt=500)
