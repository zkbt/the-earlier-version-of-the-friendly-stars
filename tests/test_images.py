from thefriendlystars import *
from thefriendlystars.panels import *

directory = 'examples'
mkdir(directory)


def test_skyview():
    star = get('LHS 1140')
    i = DSS1b(star)
    i.imshow()
    plt.savefig(os.path.join(directory,'example-astroquery-image.pdf'))

def test_tessffi():
    star = get('LHS 1140')
    i = TESSImage(star)
    i.imshow()
    plt.savefig(os.path.join(directory,'example-tess-image.pdf'))
