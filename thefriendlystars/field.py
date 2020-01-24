from .imports import *
from .constellations.constellation import *
from . import io


unit = 'arcmin'

# a shortcut getting the coordinates for an object, by its name
get = SkyCoord.from_name

def clean_tic_string(s):
    '''
    Be sure to strip the "TIC" out of a TIC.
    '''
    return int(str(s).lower().replace('tic', '').replace(' ', ''))

def get_one_tic_as_constellation(tic):
    '''
    Use the MAST archive to download a SkyCoord for one
    star from the TESS Input Catalog.

    '''

    # import Catalogs only when we need it
    # (otherwise, we'll need the internet to ever run tfs)
    from astroquery.mast import Catalogs

    # download that TIC from the archive
    t = Catalogs.query_criteria(catalog="Tic", ID=clean_tic_string(tic))[0]

    # the 'ra' and 'dec' columns were propagated to J2000
    # (https://outerspace.stsci.edu/display/TESS/TIC+v8+and+CTL+v8.xx+Data+Release+Notes)
    obstime='J2000.0'

    # define a sky coord, with proper motions and a time

    s = Constellation.from_coordinates(  ra=t['ra']*u.deg,
                                         dec=t['dec']*u.deg,
                                         pm_ra_cosdec=t['pmRA']*u.mas/u.year,
                                         pm_dec=t['pmDEC']*u.mas/u.year,
                                         obstime='J2000.0')

    return s

def parse_center(center):
    '''
    Flexible wrapper to ensure we return a SkyCoord center.
    '''
    if type(center) == str:
        if center[0:3].lower() == 'tic':
            tic = clean_tic_string(center[3:])
            return get_one_tic_as_constellation(tic).skycoord
        else:
            return SkyCoord.from_name(center)
    else:
        return center

class Field(Talker):
    '''
    Objects the inherit from this Field have
    a center and radius, and basic capabiltiies
    in converting from celestial to local
    tangent-plane coordinates.
    '''

    def __init__(self, center, radius=3*u.arcmin):
        '''
        Initialize a Field, which has (at least) a center and a radius.

        Parameters
        ----------

        center : Field, SkyCoord, string
            If initializing with a Field, the center and radius and
            coordinates will be pulled directly from that Field
            (so that coordinates don't need to be re-queried).

            If initialized with a SkyCoord or a string, the coordinates
            will need to be downloaded from scratch.
        radius : astropy.units.quantity.Quantity
            The radius out to which the field should stretch.
        '''

        # if initialized with an existing field, pull everything from that
        if isinstance(center, Field):
            field = center
            self.center = field.center
            self.radius = field.radius
            self._coordinate_center = field.coordinate_center
        else:
            self.center = center
            self.radius = radius


    def __repr__(self):
        '''
        How should this field be represented as a string?
        '''

        # what's the name of this survey?
        name = self.__class__.__name__

        # what's the target of this particular image
        if type(self.center) == str:
            target = self.center.replace(' ','')
        elif isinstance(self.center, SkyCoord):
            target = self.center.to_string('hmsdms').replace(' ', '')
        elif self.center is None:
            target='centerless'
        else:
            raise ValueError("It's not totally clear what the center should be!")

        # what's the radius out to which this image searched?
        if self.radius is None:
            size = 'radiusless'
        elif np.isfinite(self.radius):
            size = f"{self.radius.to('arcsec'):.0f}"
        else:
            size = np.inf # maybe replace with search criteria?

        return f'<{name}-{target}-{size}>'.replace(' ', '')

    @property
    def coordinate_center(self):
        '''
        The center of this field,
        as an astropy SkyCoord.
        '''
        try:
            return self._coordinate_center
        except AttributeError:
            self._coordinate_center = parse_center(self.center)
            return self._coordinate_center

    @property
    def ra_center(self):
        '''
        The RA of the center of this field.
        '''
        return self.coordinate_center.ra

    @property
    def dec_center(self):
        '''
        The DEC of the center of this field.
        '''
        return self.coordinate_center.dec

    def celestial2local(self, ra, dec):
        '''
        Convert from celestial coordinates (RA, DEC)
        to local plane coordinates (xi, eta).

        Parameters
        ----------
        ra, dec
            Both must have units associated

        # following http://www.gemini.edu/documentation/webdocs/tn/tn-ps-g0045.ps

        '''


        # unit converts from deg to radians
        theta0 = self.ra_center#*np.pi/180
        theta = ra#*np.pi/180
        dtheta = theta-theta0
        phi = dec#*np.pi/180
        phi0 = self.dec_center#*np.pi/180

        # calculate xi and eta
        d = np.sin(phi)*np.sin(phi0) + np.cos(phi)*np.cos(phi0)*np.cos(dtheta)
        xi = np.cos(phi)*np.sin(dtheta)/d
        eta = (np.sin(phi)*np.cos(phi0) - np.cos(phi)*np.sin(phi0)*np.cos(dtheta))/d

        # convert back to degrees
        #return xi*180/np.pi, eta*180/np.pi
        return (xi*u.radian).to(unit), (eta*u.radian).to(unit)

    def local2celestial(self, xi, eta):
        '''
        Convert from local coordinates (xi, eta)
        to celestial coordinates (RA, Dec),
        both in degrees.

        (A little kludgy; could be more accurate?)
        '''

        # unit conversions
        theta0 =  self.ra_center#*np.pi/180
        phi0 = self.dec_center#*np.pi/180
        eta_kludge = np.sin(eta)
        xi_kludge = np.sin(xi)
        # calculate ra and dec
        d = np.cos(phi0)- eta_kludge*np.sin(phi0)
        theta = np.arctan2(xi_kludge, d) + theta0
        phi = np.arctan2(np.sin(phi0) + eta_kludge*np.cos(phi0), np.sqrt(xi_kludge**2 + d**2))

        # convert back to degrees
        #return theta*180/np.pi, phi*180/np.pi
        return theta.to('deg'), phi.to('deg')

    @property
    def filename(self):
        '''
        What's the default filename for this object?
        '''

        return os.path.join(io.cache_directory, f'{self}.pickled')

    def save(self):
        '''
        Save the hard-to-load data.
        '''
        if io.cache:
            mkdir(io.cache_directory)
            with open(self.filename, 'wb') as file:
                pickle.dump(self._downloaded, file)
                print(f'saved file to {self.filename}')

    def load(self):
        '''
        Load the hard-to-download data.
        '''
        with open(self.filename, 'rb') as file:
            self._downloaded = pickle.load(file)
            print(f'loaded file from {self.filename}')

    def populate(self):
        '''
        Populate the data of this object,
        either by loading a pre-existing local file
        or by downloading from the web.
        '''
        try:
            # load from a local file
            self.load()
        except (IOError, EOFError):
            # download the necessary data from online
            print(f'downloading new data to initialize {self}')
            self.download()
            self.save()
