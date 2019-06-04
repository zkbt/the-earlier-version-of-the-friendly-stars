from thefriendlystars import *
from thefriendlystars.panels import *

directory = 'examples'
mkdir(directory)


def test_skyview():
    i = DSS1b('LHS 1140')
    i.imshow()
    plt.savefig(os.path.join(directory,'example-astroquery-image.pdf'))

def test_tessffi():
    i = TESS('LHS 1140')
    i.imshow()
    plt.savefig(os.path.join(directory,'example-tess-image.pdf'))
