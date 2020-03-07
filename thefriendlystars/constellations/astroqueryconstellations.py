"""
NOT YET IMPLEMENTED???
"""

from .catalogconstellation import *


class astroqueryConstellation(CatalogConstellation):
    '''
    A base class for all queries that
    depend on astroquery
    '''

    catalog = None
    name = 'astroquery'
    color = 'black'
    defaultfilter = None # this is the default filter to display
    filters = None
    magnitudelimit = 20.0
    identifier_keys = []
    error_keys = []
    epoch = 2000.0

    def download(self, **kw):
        '''
        Download a cone search of stars in this field.
        This populates the hidden ._downloaded table.
        '''

        if self.center is None:
            return self.download_allsky(**kw)

        # run the query
        from astroquery.mast import Catalogs

        table = Catalogs.query_region(self.center_skycoord,
                                      radius=self.radius,
                                      catalog=self.catalog)

        # store the search parameters in this object
        self._downloaded = self.standardize_table(table)
        self._downloaded.meta['center'] = self.center
        self._downloaded.meta['radius'] = self.radius
        self._downloaded.meta['magnitudelimit'] = self.magnitudelimit

    def download_allsky(self, **kw):
        raise NotImplementedError("""
        Alas, this catalog search does not have a handy wrapper
        for conducting an all-sky search yet. Sorry!""")

    """
    @classmethod
    def from_sky(cls, distancelimit=15, magnitudelimit=18):
        '''
        Create a Constellation from a criteria search of the whole sky.

        Parameters
        ----------
        distancelimit : float
            Maximum distance (parsecs).
        magnitudelimit : float
            Maximum magnitude (for Gaia G).

        '''

        # define a query for cone search surrounding this center
        criteria = []
        if distancelimit is not None:
            criteria.append('parallax >= {}'.format(1000.0/distancelimit))
        if magnitudelimit is not None:
            criteria.append('phot_g_mean_mag <= {}'.format(magnitudelimit))

        allskyquery = '''{} WHERE {}'''.format(cls.basequery, ' and '.join(criteria))
        print(allskyquery)

        # run the query
        print('querying Gaia DR2, for distance<{} and G<{}'.format(distancelimit, magnitudelimit))
        table = query(allskyquery)

        # store the search parameters in this object
        c = cls(cls.standardize_table(table))

        c.standardized.meta['query'] = allskyquery
        c.standardized.meta['magnitudelimit'] = magnitudelimit
        c.standardized.meta['distancelimit'] = distancelimit

        #c.distancelimit = distancelimit
        #c.magnitudelimit = magnitudelimit or c.magnitudelimit
        return c
    """

    @classmethod
    def standardize_table(cls, table):
        '''
        Extract objects from an astroquery table.
        '''

        raise NotImplementedError("""
        Alas, this catalog search has not yet defined a way
        to standardize the columns that have been downloaded
        from the archive. Someone should really get on that!
        """)
#class TIC(astroqueryConstellation):
#    catalog = 'TIC'
