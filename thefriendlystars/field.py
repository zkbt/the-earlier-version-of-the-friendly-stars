from .imports import *
from .centers import *
from . import io

unit = 'arcmin'


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

        Talker.__init__(self)

        # if initialized with an existing field, pull everything from that
        if isinstance(center, Field):
            field = center
            self.center = field.center
            self.radius = field.radius
            self._center_constellation = field.center_constellation
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

        return f'{name}-{target}-{size}'.replace(' ', '')

    def set_epoch(self, epoch):
        '''
        If this field center is defined with some proper motions,
        move the center to a particular time.
        '''

        self._center_constellation = self.center_constellation.at_epoch(epoch)

    @property
    def center_constellation(self):
        '''
        The center of this field,
        as a Constellation object.
        '''
        try:
            return self._center_constellation
        except AttributeError:
            self._center_constellation = parse_center(self.center)
            return self._center_constellation

    @property
    def center_skycoord(self):
        '''
        The center of this field,
        as a Constellation object.
        '''
        return self.center_constellation.skycoord

    @property
    def center_ra(self):
        '''
        The RA of the center of this field.
        '''
        return self.center_constellation.ra

    @property
    def center_dec(self):
        '''
        The DEC of the center of this field.
        '''
        return self.center_constellation.dec

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
        theta0 = self.center_ra#*np.pi/180
        theta = ra#*np.pi/180
        dtheta = theta-theta0
        phi = dec#*np.pi/180
        phi0 = self.center_dec#*np.pi/180

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
        theta0 =  self.center_ra#*np.pi/180
        phi0 = self.center_dec#*np.pi/180
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
                self.speak(f'saved file to {self.filename}')

    def load(self):
        '''
        Load the hard-to-download data.
        '''
        with open(self.filename, 'rb') as file:
            self._downloaded = pickle.load(file)
            self.speak(f'loaded file from {self.filename}')

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
            self.speak(f'downloading new data for {self}')
            self.download()
            self.save()
