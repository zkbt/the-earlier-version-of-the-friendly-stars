from thefriendlystars.constellations.gaia import *

def test_cone():
    cone = Gaia.from_cone('GJ1132')
    cone.finder()
    plt.savefig('example-gaia-cone.pdf')

def test_sky():
    sky = Gaia.from_sky(distancelimit=15)
    sky.allskyfinder()
    plt.savefig('example-gaia-allsky.pdf')

def test_motion():
    sky = Gaia.from_sky(distancelimit=15)
    sky.animate('example-gaia-animation.mp4', epochs=[0,10000], dt=500)
