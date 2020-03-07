from .astroqueryconstellations import *
from ..centers import *

class TIC(astroqueryConstellation):
    name = 'TIC'
    color = 'crimson'
    catalog = 'Tic'
    filters = ['B', 'V', 'u', 'g', 'r', 'i', 'z', 'J', 'H', 'K', 'w1', 'w2', 'w3', 'w4', 'T']
    defaultfilter = 'T'
    identifier_keys = ['TIC', '2MASS', 'GaiaDR2', 'KIC']

    @classmethod
    def standardize_table(cls, table):
        '''
        Extract objects from the astroquery TIC table.
        '''

        table = Table(table)

        tic_epoch = 2000.0

        # tidy up quantities, setting motions to 0 if poorly defined
        for key in ['pmRA', 'pmDEC', 'plx']:
            bad = (np.isfinite(table[key]) == False)# | (table[key].mask)
            table[key][bad] = 0.0

        # replace really bad parallaxes
        bad = (table['plx']/table['e_plx'] < 1)# | (table['plx'].mask)
        table['plx'][bad] = np.nan
        distance = 1000*u.pc/table['plx']


        #distance[bad] = 10000*u.pc#np.nanmax(distance)
        identifiers  = {'TIC-id':table['ID'],
                        '2MASS-id':table['TWOMASS'],
                        'GaiaDR2-id':table['GAIA'],
                        'KIC-id':table['KIC']}

        # populate the coordinates
        N = len(table['ra'])
        coordinates = dict(  ra=table['ra']*u.deg,
                             dec=table['dec']*u.deg,
                             pm_ra_cosdec=table['pmRA']*u.mas/u.year,
                             pm_dec=table['pmDEC']*u.mas/u.year,
                             #radial_velocity=table['radial_velocity'].data*u.km/u.s,
                             distance=distance, # weirdly, messed with RA + Dec signs if parallax is zero
                             obstime=Time([tic_epoch]*N, format='decimalyear'))

        # populate the magnitudes
        magnitudes = {k+'-mag':table[f'{k}mag'.format(k)] for k in cls.filters}

        # create a stacked standardized table
        standardized = hstack([Table(identifiers),
                               Table(coordinates),
                               Table(magnitudes)])

        standardized.meta['catalog'] = 'TIC'

        return standardized

class SingleTIC(TIC):

    def __init__(self,
                 center,
                 radius=3*u.arcmin,
                 **kw):
        '''
        Initialize a Constellation as a search for a single entry in the TIC.

        Parameters
        ----------
        center : SkyCoord object, or str
            The center around which the query will be made.
            If a str, SkyCoord will be resolved with SkyCoord.from_name
            If None, an all-sky query will be attempted.
        radius : float, with units of angle
            The angular radius for the query.
            If np.inf, an all-sky query will be attempted.
        **kw : dict
            Any extra keyword arguments will be passed to download
            and/or download_allsky
        '''

        Talker.__init__(self)
        
        tic = clean_tic_string(center)

        self.center = f'TIC{tic}'
        self.radius = 0*u.arcmin

        # poulate the ._downloaded attribute (either by loading or downloading)
        self.populate()

        # feed a standardized table as inputs to create a constellation
        Constellation.__init__(self, self._downloaded,
                               center=self.center, radius=self.radius)

    def download(self, **kw):
        '''
        Download a cone search of stars in this field.
        This populates the hidden ._downloaded table.
        '''

        # run the query
        from astroquery.mast import Catalogs

        tic = clean_tic_string(self.center)
        table = Catalogs.query_criteria(ID=tic,
                                        catalog=self.catalog)[0]

        # store the search parameters in this object
        self._downloaded = self.standardize_table(table)
        self._downloaded.meta['center'] = self.center
        self._downloaded.meta['radius'] = self.radius
