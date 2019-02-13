from thefriendlystars import *
from thefriendlystars.panels import *

plt.ion()

def test_skyview():
    star = get('LHS 1140')
    i = skyviewImage(star)
    i.imshow()
    return i


if __name__ == '__main__':

    i = test_skyview()
