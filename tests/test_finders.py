'''
Test basic finder capabilities.
'''
from thefriendlystars.imports import *
from thefriendlystars.finders import *

directory = 'examples'
mkdir(directory)

def test_panel():
    '''
    Can we create a simple panel.
    '''
    center = SkyCoord('00h44m59.3315s-15d16m17.5431s')
    p = Panel(center)
    p.plot()
    plt.savefig(os.path.join(directory, 'example-panel.pdf'))


def test_grid():
    '''
    Can we create a grid of multiple images?
    '''

    center = SkyCoord('00h44m59.3315s-15d16m17.5431s')
    f = Finder(center)
    f.plot()

    plt.savefig(os.path.join(directory, 'example-finder-grid.pdf'))

    return f


if __name__ == '__main__':
    # pull out anything that starts with `test_`
    d = locals()
    tests = [x for x in d if 'test_' in x]
    # run those functions and save their output
    outputs = {k.split('_')[-1]:d[k]()
               for k in tests}
