'''
Test basic constellation abilities.
'''

from thefriendlystars.imports import *
from thefriendlystars.constellations import *

directory = 'examples'
mkdir(directory)

def create_fake(N=5):
    '''
    Create a simple fake Constellation with random stars.
    '''
    # make sure we can initialize a constellation from coordinates
    ra = np.random.uniform(0, 360, N)*u.deg
    dec = np.random.uniform(-90,90, N)*u.deg
    mag = np.random.triangular(0, 20, 20, N)
    sky = Constellation.from_coordinates(ra=ra, dec=dec, mag=mag)
    return sky


def create_fake_with_pm(N=5):
    '''
    Create a simple fake Constellation with random stars.
    '''
    # make sure we can initialize a constellation from coordinates
    ra = np.random.uniform(0, 360, N)*u.deg
    dec = np.random.uniform(-90,90, N)*u.deg
    mag = np.random.triangular(0, 20, 20, N)
    pm_ra_cosdec = np.random.uniform(-1000, 1000, N)*u.mas/u.year
    pm_dec = np.random.uniform(-1000, 1000, N)*u.mas/u.year
    obstime = np.ones(N)*2000*u.year

    sky = Constellation.from_coordinates(ra=ra, dec=dec, mag=mag,
                                         pm_ra_cosdec=pm_ra_cosdec,
                                         pm_dec=pm_dec,
                                         obstime=obstime)
    return sky

def test_attributes():
    '''
    Can we access coordinates as attributes?
    '''

    sky = create_fake()

    # make sure we can access basic attributes
    print(sky.ra)
    print(sky.dec)
    print(sky.epoch)
    print(sky.meta)

def test_SkyCoord():
    '''
    Can we pull out SkyCoords from this constellation?
    '''
    sky = create_fake()

    sky.as_SkyCoord().icrs

def test_subsets():
    '''
    Can we access various indexed and sliced subsets of this?
    '''

    sky = create_fake()

    # make sure we can access basic attributes
    print(sky['0'])
    print(sky[0])
    print(sky[['0','2']])
    print(sky[[0,2]])
    print(sky[:])

def test_tables():
    '''
    Can we access sub-tables?
    '''

    sky = create_fake()

    # make sure we can access the subtables
    print(sky.coordinates_table)
    print(sky.identifiers_table)
    print(sky.magnitudes_table)
    print(sky.errors_table)

def test_outputinput():
    '''
    Can we write and read catalogs?
    '''

    sky = create_fake()

    filename = os.path.join(directory, 'example-custom.txt')

    # make sure we can write this constellation to a file
    sky.write_to_text(filename)

    #
    # new = Constellation.from_text(filename)
    # FIXME -- we should make sure we can still access everything in this "new"

def test_graphics():
    '''
    Can we output this constellation in different formats?
    '''

    sky = create_fake_with_pm()

    # make sure we can make a finder chart of these stars
    sky.finder()
    plt.savefig(os.path.join(directory, 'finder-custom.pdf'))

    # make sure we can make an all-sky finder chart of these stars
    sky.allskyfinder()
    plt.savefig(os.path.join(directory, 'allsky-finder-custom.pdf'))

    # make sure we can animate
    sky.animate(filename=os.path.join(directory, 'animated-custom.mp4'), dt=30)

def test_crossmatch():
    '''
    Can we cross match two catalogs to each other?
    '''

    # create a fake catalog
    sky = create_fake_with_pm()

    # check that I can recovered everything by matching with myself
    is_matched, indices = sky.cross_match_to(sky)
    assert(np.all(is_matched))

    # ...no matter what the order
    is_matched, indices = sky.cross_match_to(sky[::-1])
    assert(np.all(is_matched))

def test_propermotions():
    '''
    Can we propagate the proper motions?
    '''

    sky = create_fake_with_pm()
    sky.at_epoch(2010.0)
    sky.at_epoch(2010.0*u.year)
    sky.at_epoch(Time('2010-01-01'))

    projected = sky.at_epoch(2010.0)
    assert(np.any(projected.ra != sky.ra))
    assert(np.any(projected.dec != sky.dec))
    assert(np.any(projected.obstime != sky.obstime))

    sky = create_fake()
    projected = sky.at_epoch(2010.0)
    assert(np.any(projected.ra == sky.ra))
    assert(np.any(projected.dec == sky.dec))
    assert(np.any(projected.obstime == sky.obstime))

if __name__ == '__main__':
    # pull out anything that starts with `test_`
    d = locals()
    tests = [x for x in d if 'test_' in x]
    # run those functions and save their output
    outputs = {k.split('_')[-1]:d[k]()
               for k in tests}
