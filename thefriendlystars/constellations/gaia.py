from .constellation import *

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



class Gaia(Constellation):
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

    def __init__(self,
                 center,
                 radius=3*u.arcmin,
                 **kw):
        '''
        Initialize a Constellation from a cone search of the sky,
        characterized by a positional center and a radius from it.

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


        # assign the center and the radius for this cone
        self.center = center
        self.radius = radius

        # parse the ways in which someone could be asking for an all-sky query
        if np.isfinite(self.radius) is False:
            self.center = None
        if self.center is None:
            self.radius = np.inf

        # poulate the ._downloaded attribute (either by loading or downloading)
        self.populate()

        # feed a standardized table as inputs to create a constellation
        Constellation.__init__(self, self._downloaded)


    def download(self, **kw):
        '''
        Download a cone search of stars in this field.
        This populates the hidden ._downloaded table.
        '''

        center = self.center

        if center is None:
            self.download_allsky(**kw)

        else:
            # create a SkyCoord from the center
            center_coord = parse_center(center)


            # define a query for cone search surrounding this center
            conequery = """{} WHERE CONTAINS(POINT('ICRS',gaiadr2.gaia_source.ra,gaiadr2.gaia_source.dec),CIRCLE('ICRS',{},{},{}))=1 and phot_g_mean_mag < {}""".format(self.basequery, center_coord.ra.deg, center_coord.dec.deg, self.radius.to(u.deg).value, self.magnitudelimit)
            #print(conequery)

            # run the query
            #print('querying Gaia DR2, centered on {} with radius {}, for G<{}'.format(center, radius, magnitudelimit))
            table = query(conequery)

            # store the search parameters in this object
            self._downloaded = self.standardize_table(table)

            self._downloaded.meta['query'] = conequery
            self._downloaded.meta['center'] = center_coord
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

        allskyquery = """{} WHERE {}""".format(self.basequery, ' and '.join(criteria))

        # run the query
        print('querying Gaia DR2, for distance<{} and G<{}'.format(distancelimit, magnitudelimit))
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

        # create skycoord objects
        coordinates = dict(  ra=table['ra'].data*u.deg,
                             dec=table['dec'].data*u.deg,
                             pm_ra_cosdec=table['pmra'].data*u.mas/u.year,
                             pm_dec=table['pmdec'].data*u.mas/u.year,
                             radial_velocity=table['radial_velocity'].data*u.km/u.s,
                             distance=distance, # weirdly, messed with RA + Dec signs if parallax is zero
                             obstime=cls.epoch*np.ones(len(table))*u.year)#Time(, format='decimalyear'))

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
