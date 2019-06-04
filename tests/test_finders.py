'''
Test basic finder capabilities.
'''
from thefriendlystars.imports import *
from thefriendlystars.finders import *

directory = 'examples'
mkdir(directory)

def test_panel():
    '''
    Can we create a panel
    '''
    p = Panel('LHS 1140')
    p.plot()
    plt.savefig(os.path.join(directory, 'example-panel.pdf'))



def test_grid():
    '''
    Can we create a grid of multiple images?
    '''
    f = Finder('LHS 1140')
    f.plotGrid()
    #f.ax['DSS2 Red'].get_shared_x_axes().join(f.ax['DSS2 Red'], f.ax['DSS2 Blue'])

    plt.savefig(os.path.join(directory, 'example-finder-grid.pdf'))

    return f
