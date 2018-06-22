from .constellation import *
import astroquery.mast

class GALEX(Constellation):
    name = 'GALEX'
    color = 'orchid'

    def coneSearch(self, center, radius=3*u.arcmin, magnitudelimit=25):
        '''
        Run a cone search of the GALEX archive
        '''


        self.magnitudelimit = magnitudelimit

        # run the query
        self.speak('querying GALEX, centered on {} with radius {}'.format(center, radius, magnitudelimit))

        coordinatetosearch = '{0.ra.deg} {0.dec.deg}'.format(center)
        table = astroquery.mast.Catalogs.query_region(coordinates=center, radius=radius, catalog='GALEX')



        # the gaia DR2 epoch is 2015.5
        epoch = 2005#???

        # create skycoord objects
        self.coordinates = coord.SkyCoord(  ra=table['ra'].data*u.deg,
                                        dec=table['dec'].data*u.deg,
                                        obstime=Time(epoch, format='decimalyear'))

        self.magnitudes = dict(NUV=table['nuv_mag'].data, FUV=table['fuv_mag'].data)
        self.magnitude = self.magnitudes['NUV']

class TIC(Constellation):
    name = 'TIC'
    color = 'green'

    def coneSearch(self, center, radius=3*u.arcmin, magnitudelimit=25):
        '''
        Run a cone search of the GALEX archive
        '''


        self.magnitudelimit = magnitudelimit

        # run the query
        self.speak('querying TIC, centered on {} with radius {}'.format(center, radius, magnitudelimit))

        coordinatetosearch = '{0.ra.deg} {0.dec.deg}'.format(center)
        table = Catalogs.query_region(coordinates=center, radius=radius, catalog='TIC')



        # the gaia DR2 epoch is 2015.5
        epoch = 2000#???

        # create skycoord objects
        self.coordinates = coord.SkyCoord(  ra=table['ra'].data*u.deg,
                                        dec=table['dec'].data*u.deg,
                                        obstime=Time(epoch, format='decimalyear'))

        self.magnitudes = dict(T=table['Tmag'].data)
        self.magnitude = self.magnitudes['T']





class TwoMass(Gaia):
    '''A catalog for 2MASS, using the Gaia-archive hosted search.'''

    name = '2MASS - J'
    color = 'orange'
    zorder = -1
    def coneSearch(self, center, radius=3*u.arcmin, magnitudelimit=20):
        '''
        Run a cone search of the Gaia DR2.
        '''


        self.magnitudelimit = magnitudelimit

        # define a query for cone search surrounding this center
        conequery = """SELECT designation, ra, dec, j_m, h_m, ks_m, j_date FROM gaiadr1.tmass_original_valid WHERE CONTAINS(POINT('ICRS',ra,dec),CIRCLE('ICRS',{},{},{}))=1 and j_m < {}""".format(center.ra.deg, center.dec.deg, radius.to(u.deg).value, magnitudelimit)


        # run the query
        self.speak('querying 2MASS, centered on {} with radius {}, for J<{}'.format(center, radius, magnitudelimit))
        table = self.query(conequery)




        # create skycoord objects
        self.coordinates = coord.SkyCoord(  ra=table['ra'].data*u.deg,
                                        dec=table['dec'].data*u.deg,
                                        obstime=Time(table['j_date'].data, format='jd'))

        self.magnitudes = dict(         J=table['j_m'].data,
                                        H=table['h_m'].data,
                                        Ks=table['ks_m'].data)
        self.magnitude = self.magnitudes['J']
