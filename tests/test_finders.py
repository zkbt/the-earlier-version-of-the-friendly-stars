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

    center = SkyCoord('00h44m59.3315s-15d16m17.5431s')
    f = Finder(center)
    f.plot_grid()
    
    plt.savefig(os.path.join(directory, 'example-finder-grid.pdf'))

    return f
