from thefriendlystars.imports import *
from thefriendlystars import *
from thefriendlystars.panels import *

directory = 'examples'
mkdir(directory)


def test_skyview():
    i = DSS1b('LHS 1140')
    plt.figure()
    i.imshow()
    plt.savefig(os.path.join(directory,'example-astroquery-image.pdf'))

def test_tessffi():
    i = TESS('LHS 1140')
    plt.figure()
    i.imshow()
    plt.savefig(os.path.join(directory,'example-tess-image.pdf'))

if __name__ == '__main__':
    # pull out anything that starts with `test_`
    d = locals()
    tests = [x for x in d if 'test_' in x]
    # run those functions and save their output
    outputs = {k.split('_')[-1]:d[k]()
               for k in tests}
