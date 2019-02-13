from thefriendlystars.finders import *
plt.ion()
def test_grid():
    f = Finder('LHS 1140')
    f.populateImagesFromSurveys()
    f.plotGrid()
    f.ax['DSS2 Red'].get_shared_x_axes().join(f.ax['DSS2 Red'], f.ax['DSS2 Blue'])
    return f

if __name__ == '__main__':

    f = test_grid()
