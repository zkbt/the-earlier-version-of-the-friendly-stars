from .catalogconstellation import *

def query(query):
    '''
    Send an ADQL query to the Gaia archive,
    wait for a response,
    and hang on to the results.
    '''

    import astroquery.gaia

    # send the query to the Gaia archive
    with warnings.catch_warnings() :
        warnings.filterwarnings("ignore")

        _gaia_job = astroquery.gaia.Gaia.launch_job(query)

        # return the table of results
        return _gaia_job.get_results()


class Gaia(CatalogConstellation):
    '''
    Gaia catalog contains sources from Gaia DR2,
    including proper motions and parallaxes.
    '''

    name = 'Gaia'
    color = 'black'
    defaultfilter = 'G' # this is the default filter to display
    filters = ['G', 'RP', 'BP']
    basequery = 'SELECT source_id,ra,ra_error,dec,dec_error,pmra,pmra_error,pmdec,pmdec_error,parallax,parallax_error,phot_g_mean_mag,phot_bp_mean_mag,phot_rp_mean_mag,radial_velocity,radial_velocity_error,phot_variable_flag,teff_val,a_g_val FROM gaiadr2.gaia_source'
    magnitudelimit = 20.0
    identifier_keys = ['GaiaDR2']
    error_keys = ['distance', 'pm_ra_cosdec', 'pm_dec', 'radial_velocity']
    epoch = 2015.5

    def download(self, **kw):
        '''
        Download a cone search of stars in this field.
        This populates the hidden ._downloaded table.
        '''


        if self.center is None:
            return self.download_allsky(**kw)

        # define a query for cone search surrounding this center
        conequery = f"""
        {self.basequery} WHERE
        CONTAINS(POINT('ICRS',
                       gaiadr2.gaia_source.ra,
                       gaiadr2.gaia_source.dec),
                 CIRCLE('ICRS',
                        {self.center_skycoord.ra.deg},
                        {self.center_skycoord.dec.deg},
                        {self.radius.to(u.deg).value}))=1
            AND phot_g_mean_mag < {self.magnitudelimit}"""

        # run the query
        self.speak(conequery)
        table = query(conequery)

        # store the search parameters in this object
        self._downloaded = self.standardize_table(table)

        self._downloaded.meta['query'] = conequery
        self._downloaded.meta['center'] = self.center_skycoord
        self._downloaded.meta['radius'] = self.radius
        self._downloaded.meta['magnitudelimit'] = self.magnitudelimit

    def download_allsky(self, distancelimit=15, magnitudelimit=18):
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

        allskyquery = f"""
        {self.basequery} WHERE
        {' and '.join(criteria)}"""

        # run the query
        table = query(allskyquery)

        # standardize the output
        self._downloaded = self.standardize_table(table)

        self._downloaded.meta['query'] = allskyquery
        self._downloaded.meta['magnitudelimit'] = magnitudelimit
        self._downloaded.meta['distancelimit'] = distancelimit

    @classmethod
    def standardize_table(cls, table):
        '''
        Extract objects from a Gaia DR2 table.

        Parameters
        ----------
        table : astropy.table.Table
            The data downloaded from a Gaai DR2 query.
        '''


        # tidy up quantities, setting motions to 0 if poorly defined
        for key in ['pmra', 'pmdec', 'parallax', 'radial_velocity']:
            bad = table[key].mask
            table[key][bad] = 0.0

        bad = table['parallax']/table['parallax_error'] < 1
        bad += table['parallax'].mask
        table['parallax'][bad] = np.nan
        distance = 1000*u.pc/table['parallax'].data

        distance[bad] = 10000*u.pc#np.nanmax(distance)
        identifiers  = {'GaiaDR2-id':table['source_id']}

        N = len(table['ra'])
        # create skycoord objects
        coordinates = dict(  ra=table['ra'].data*u.deg,
                             dec=table['dec'].data*u.deg,
                             pm_ra_cosdec=table['pmra'].data*u.mas/u.year,
                             pm_dec=table['pmdec'].data*u.mas/u.year,
                             radial_velocity=table['radial_velocity'].data*u.km/u.s,
                             distance=distance, # weirdly, messed with RA + Dec signs if parallax is zero
                             obstime=Time(cls.epoch*np.ones(N), format='decimalyear'))#Time(, format='decimalyear'))

        magnitudes = {k+'-mag':table['phot_{}_mean_mag'.format(k.lower())].data for k in cls.filters}


        errors = dict(distance= distance*(table['parallax_error'].data/table['parallax'].data),
                      pm_ra_cosdec=table['pmra_error'].data*u.mas/u.year,
                      pm_dec=table['pmdec_error'].data*u.mas/u.year,
                      radial_velocity=table['radial_velocity_error'].data*u.km/u.s)

        error_table = Table(data=[errors[k] for k in cls.error_keys],
                            names=[k+'-error' for k in cls.error_keys])


        #for key in ['pmra', 'pmdec', 'parallax', 'radial_velocity']:
        #        bad = table[key].mask
        #        table[key][bad] = 0.0


        standardized = hstack([Table(identifiers),
                               Table(coordinates),
                               Table(magnitudes),
                               error_table])

        standardized.meta['catalog'] = 'Gaia'

        return standardized
