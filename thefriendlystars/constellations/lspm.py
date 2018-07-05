from .constellation import *
from astroquery.vizier import Vizier


class LSPM(Constellation):
    '''
    LSPM contains sources from the LSPM-North catalog,
    including proper motions and estimated V magnitudes.
    '''

    name = 'LSPM'
    color = 'black'
    defaultfilter = 'Ve' # this is the default filter to display
    epoch = 2000.0 # the default epoch
    columns = ['LSPM', '2MASS', '_RAJ2000', '_DEJ2000', 'pmRA', 'pmDE', 'Bmag', 'Vmag', 'BJmag', 'RFmag', 'INmag', 'Jmag', 'Hmag', 'Kmag', 'Vemag', 'V-J']
    filters = ['B', 'V', 'BJ', 'RF', 'IN', 'J', 'H', 'K', 'Ve']
    identifier_keys = ['LSPM', '_2MASS']
    catalog = 'I/298/lspm_n'
    magnitudelimit = 18

    @classmethod
    def from_cone(cls, center,
                  radius=3*u.arcmin,
                  magnitudelimit=None,
                  **kw):
        '''
        Create a Constellation from a cone search of the sky,
        characterized by a positional center and a radius from it.

        Parameters
        ----------
        center : SkyCoord object
            The center around which the query will be made.
        radius : float, with units of angle
            The angular radius for the query.
        magnitudelimit : float
            The maximum magnitude to include in the download.
            (This is explicitly thinking UV/optical/IR, would
            need to change to flux to be able to include other
            wavelengths.)
        '''

        # make sure the center is a SkyCoord
        center = parse_center(center)

        criteria = {}
        if magnitudelimit is not None:
            criteria[cls.defaultfilter + 'mag'] = '<{}'.format(magnitudelimit)

        v = Vizier(columns=cls.columns,
                   column_filters=criteria)
        v.ROW_LIMIT = -1

        # run the query
        print('querying Vizier for {}, centered on {} with radius {}, for G<{}'.format(cls.name, center, radius, magnitudelimit))

        table = v.query_region(coordinates=center,
                               radius=radius,
                               catalog=cls.catalog)[0]

        # store the search parameters in this object
        c = cls(cls.standardize_table(table))
        c.standardized.meta['catalog'] = cls.catalog
        c.standardized.meta['center'] = center
        c.standardized.meta['radius'] = radius
        c.standardized.meta['magnitudelimit'] = magnitudelimit
        #c.center = center
        #c.radius = radius
        #c.magnitudelimit = magnitudelimit or cls.magnitudelimit
        return c

    @classmethod
    def from_sky(cls, magnitudelimit=None):
        '''
        Create a Constellation from a criteria search of the whole sky.

        Parameters
        ----------
        magnitudelimit : float
            Maximum magnitude (for Ve = "estimated V").
        '''


        # define a query for cone search surrounding this center

        criteria = {}
        if magnitudelimit is not None:
            criteria[cls.defaultfilter + 'mag'] = '<{}'.format(magnitudelimit)

        v = Vizier(columns=cls.columns,
                   column_filters=criteria)
        v.ROW_LIMIT = -1

        # run the query
        print('querying Vizier for {}, for {}<{}'.format(cls.name, cls.defaultfilter, magnitudelimit))

        table = v.query_constraints(catalog=cls.catalog, **criteria)[0]

        # store the search parameters in this object
        c = cls(cls.standardize_table(table))
        c.standardized.meta['catalog'] = cls.catalog
        c.standardized.meta['criteria'] = criteria
        c.standardized.meta['magnitudelimit'] = magnitudelimit or c.magnitudelimit
        #c.magnitudelimit = magnitudelimit or c.magnitudelimit
        return c

    @classmethod
    def standardize_table(cls, table):
        '''
        Extract objects from a Gaia DR2 table.
        '''

        print(cls)
        identifiers = {n+'-id':table[n] for n in cls.identifier_keys}

        # create skycoord objects
        N = len(table)
        coordinates = dict(  ra=table['_RAJ2000'].data.data*u.deg,
                             dec=table['_DEJ2000'].data.data*u.deg,
                             pm_ra_cosdec=table['pmRA'].data.data*u.arcsec/u.year,
                             pm_dec=table['pmDE'].data.data*u.arcsec/u.year,
                             radial_velocity=np.nan*np.ones(N)*u.km/u.s,
                             distance=np.nan*np.ones(N)*u.pc,#distance=1000*u.pc/table['parallax'].data, # weirdly, messed with RA + Dec signs if parallax is zero
                             obstime=cls.epoch*np.ones(N)*u.year)#Time(, format='decimalyear'))
        for k in coordinates:
            print(k, coordinates[k])
        magnitudes = {f+'-mag':table[f+'mag'].data for f in cls.filters}

        standardized = hstack([Table(identifiers),
                               Table(coordinates),
                               Table(magnitudes)])
        standardized.meta['catalog'] = 'Gaia'

        return standardized
