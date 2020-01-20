from .imports import *
from . import io

# a shortcut getting the coordinates for an object, by its name
get = SkyCoord.from_name

def parse_center(center):
    '''
    Flexible wrapper to ensure we return a SkyCoord center.
    '''
    if type(center) == str:
        center = get(center)
    return center

class Field(Talker):
    '''
    Objects the inherit from this Field have
    a center and radius, and basic capabiltiies
    in converting from celestial to local
    tangent-plane coordinates.
    '''
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
            target='allsky'
        else:
            raise ValueError("It's not totally clear what the center should be!")

        # what's the radius out to which this image searched?
        if np.isfinite(self.radius):
            size = self.radius.to('arcsec')
        else:
            size = np.inf # maybe replace with search criteria?

        return f'{name}-{target}-{size:.0f}'.replace(' ', '')

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
        return (xi*u.radian).to('arcmin'), (eta*u.radian).to('arcmin')

    def local2celestial(self, xi, eta):
        '''
        Convert from local coordinates (xi, eta)
        to celestial coordinates (RA, Dec),
        both in degrees.
        '''

        # unit conversions
        theta0 =  self.ra_center#*np.pi/180
        phi0 = self.dec_center#*np.pi/180

        # calculate ra and dec
        d = np.cos(phi0)- eta*np.sin(phi0)
        theta = np.arctan2(xi, d) + theta0
        phi = np.arctan2(np.sin(phi0) + eta*np.cos(phi0), np.sqrt(xi**2 + d**2))

        # convert back to degrees
        #return theta*180/np.pi, phi*180/np.pi
        return theta, phi

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
