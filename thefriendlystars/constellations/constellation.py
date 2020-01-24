from ..imports import *

def convert_epoch_to_time(epoch):
    '''
    Make sure an epoch gets converted into an astropy time.
    '''
    if type(epoch) == Time:
        t = epoch
    elif type(epoch) == u.Quantity:
        t = Time(epoch.to('year').value, format='decimalyear')
    elif type(epoch) == str:
        t = Time(epoch)
    else:
        t = Time(epoch, format='decimalyear')
    assert(type(t) == Time)
    return t

def convert_time_to_epoch(time):
    '''
    Convert an astropy time to a simple epoch number.
    '''
    return time.decimalyear

class Constellation(Talker):
    '''
    A Constellation is collection of stars
    that can be accessed through a table of
    astropy coordinates, and/or plotted
    on a Finder chart Panel.
    '''
    name = 'someconstellation'
    color = 'black'
    # epoch = 2000.0 # the default epoch
    magnitudelimit = 20.0
    identifier_keys = ['object']
    filters = ['filter']
    defaultfilter = 'filter'
    error_keys = []
    coordinate_keys = ['ra', 'dec',
                       'pm_ra_cosdec', 'pm_dec',
                       'obstime',
                       'distance', 'radial_velocity']

    def __init__(self, standardized, center=None, radius=None):
        '''
        Initialize a Constellation object.

        Parameters
        ----------
        standardized : astropy.table.Table
            Must contain at least one identifier, coordinates, and at least one magnitude.
        '''

        # set up the talker for this catalog
        Talker.__init__(self)

        # create an astropy table
        self.standardized = QTable(standardized)

        # use the first identifier as the search key
        self.standardized.add_index(self.identifier_keys[0]+'-id')

        # make sure we end up with actual times for the obstimes
        #if self.obstime is not None:
        #    self.obstime = convert_epoch_to_time(self.obstime)

        # store the center and radius associated with this field
        self.center = center
        self.radius = radius

    def __getattr__(self, key):
        '''
        If an attribute/method isn't defined for a Constellation,
        look for it as a column of the standardized table.

        For example, `constellation.ra` will try to
        access `constellation.standardized['ra']`.

        Parameters
        ----------
        key : str
            The attribute we're trying to get.
        '''
        if key == 'epoch':
            epoch = np.atleast_1d(self.obstime)
            if (epoch == epoch[0]).all():
                epoch = epoch[0]
            return epoch
        elif key == 'magnitude':
            return self.standardized[self.defaultfilter + '-mag']
        elif key in self.coordinate_keys:
            try:
                x = self.standardized[key]
                if np.size(x) == 1:
                    return np.atleast_1d(x)[0]
                else:
                    return x
            except KeyError:
                return None
        elif key == 'meta':
            return self.standardized.meta
        else:
            raise AttributeError(f"""
            The attribute '.{key}' seems not to exist for this Constellation
            and doesn't have any magic tricks defined in __getattr__
            for figuring out what should be returned.
            """)

    def __getitem__(self,x):
        '''
        Define how can we extract subsets of this Constellation.

        c['a'] will pull star 'a' from the indexed ID column
        c[['a', 'b'] will pull stars 'a' and 'b' from the indexed ID column
        c[0] will pull the first star
        c[0:4] will pull the first 5 stars

        '''
        # create a trimmed table
        if type(np.atleast_1d(x)[0]) is  np.str_:
            trimmed = Table(self.standardized.loc[x])
        else:
            trimmed = Table(self.standardized[x])

        # create a new class from that trimmed table
        return self.__class__(trimmed)

    @property
    def skycoord(self):
        '''
        Create a SkyCoord object from the coordinates.
        '''
        return SkyCoord( ra=self.ra,
                         dec=self.dec,
                         pm_ra_cosdec=self.pm_ra_cosdec,
                         pm_dec=self.pm_dec,
                         obstime=self.obstime,
                         distance=self.distance,
                         radial_velocity=self.radial_velocity)

    @classmethod
    def from_coordinates(cls,   ra=None, dec=None,
                                distance=None,
                                pm_ra_cosdec=None,
                                pm_dec=None,
                                radial_velocity=None,
                                obstime=Time('J2000.0'),
                                id=None, mag=None,
                                **kwargs):
        '''
        Iniitalize a constellation object from variables that contain
        coordinates. Missing columns will be left out of the standardized
        table.

        Parameters
        ----------

        ra, dec, distance, pm_ra_cosdec, pm_dec, radial_velocity
            These must be able to initialize a SkyCoord.
        id : list, array
            Identifications for the entries.
        mag : list, array
            Magnitudes for the entries.
        **kwargs
            All arguments and keyword arguments are passed along
            to SkyCoord. They can be coordinates in the first place,
            or, for example, ra and dec with units, or any other
            inputs that can initialize a SkyCoord.
        '''

        # count the number of coordinates
        N = len(np.atleast_1d(ra))

        # make up some dummy IDs, if need be
        if id is None:
            id = ['{}'.format(i) for i in range(N)]

        # make up some dummy magnitudes, if need be
        if mag is None:
            mag = np.zeros(N)

        obstime = convert_epoch_to_time(obstime)

        # create a standardized table
        standardized = Table(data=[id, mag], names=['object-id', 'filter-mag'])

        # populate the table with every coordinate key
        for k in cls.coordinate_keys:
            if locals()[k] is not None:
                standardized[k] = locals()[k]

        # return a newly created Constellation, from these coordinates
        return cls(standardized)

    @property
    def identifiers_table(self):
        '''
        Pull out just the columns that are identifiers.
        '''

        keys = [x + '-id'
                for x in self.identifier_keys
                if x + '-id' in self.standardized.colnames]

        return self.standardized[keys]

    @property
    def magnitudes_table(self):
        '''
        Pull out just the columns that are magnitudes.
        '''
        keys = [x + '-mag'
                for x in self.filters
                if x + '-mag' in self.standardized.colnames]

        return self.standardized[keys]

    @property
    def errors_table(self):
        '''
        Pull out just the columns that are errors.
        '''
        keys = [x + '-error'
                for x in self.error_keys
                if x + '-error' in self.standardized.colnames]
        return self.standardized[keys]

    @property
    def coordinates_table(self):
        '''
        Pull out just the columns that are coordinates.
        '''

        # figure out which are just the coordinate-related columns
        available_keys = [x
                          for x in self.coordinate_keys
                          if x in self.standardized.colnames]

        # extract that table
        return self.standardized[available_keys]

    def write_to_text(self, filename=None, overwrite=True):
        '''
        Write this constellation out to a text file.
        '''

        # extract the standardized table
        table = self.standardized

        # makeu sure there's a filename
        if filename == None:
            filename = '{}.txt'.format(self.name)

        # write the constellation to a file
        self.speak('saving to {}'.format(filename))
        table.write(filename, format='ascii.ecsv', overwrite=overwrite)


    def at_epoch(self, epoch=2000):
        '''
        Return this constellation, but with positions propagated
        to another (single) given epoch.

        Parameters
        ----------
        epoch : Time, or float
            Either an astropy time, or a decimal year of the desired epoch.

        Returns
        -------
        projected : Constellation
            This constellation, propagated to the given epoch,
            with that epoch stored in the obstime attribute.
        '''

        # make a deep copy of this object
        projected = copy.deepcopy(self)

        # get the requested epoch into a quantity with units of years
        newobstime = convert_epoch_to_time(epoch)

        # calculate the time offset from the epoch(s) of the orignal coordinates
        dt = (newobstime.decimalyear - self.obstime.decimalyear)*u.year


        # calculate the new positions, propagated linearly by dt
        try:
            # if proper motions exist
            assert(np.all(self.pm_ra_cosdec is not None))
            assert(np.all(self.pm_dec is not None))

            newra = (self.ra + self.pm_ra_cosdec/np.cos(self.dec)*dt).to(u.deg)
            newdec = (self.dec + self.pm_dec*dt).to(u.deg)
        except AssertionError:
            # assume no proper motions, if they're not defined
            newra = self.ra
            newdec = self.dec
            newobstime = self.obstime
            self.speak('no proper motions were used for {}'.format(self.name))
            self.speak(f'the epoch was kept at its original {self.obstime}')

        projected.standardized['ra'] = newra
        projected.standardized['dec'] = newdec
        projected.standardized['obstime'] = newobstime

        return projected

    def plot(self, ax=None, sizescale=10, celestial2local=None, color=None, alpha=0.5, label=None, edgecolor='none', **kw):
        '''
        Plot the ra and dec of the coordinates,
        at a given epoch, scaled by their magnitude.

        (This does *not* create a new empty figure.)

        Parameters
        ----------
        sizescale : (optional) float
            The marker size for scatter for a star at the magnitudelimit.
        color : (optional) any valid color
            The color to plot (but there is a default for this catalog.)
        **kw : dict
            Additional keywords will be passed on to plt.scatter.

        Returns
        -------

        plotted : outputs from the plots
        '''
        # calculate the sizes of the stars (logarithmic with brightness?)
        size = np.maximum(sizescale*(1 + self.magnitudelimit - self.magnitude), 1)

        if ax is None:
            ax = plt.gca()

        if celestial2local is None:
            x, y = self.ra, self.dec
        else:
            x, y = celestial2local(self.ra, self.dec)
        # make a scatter plot of the RA + Dec
        scatter = ax.scatter(x, y,
                              s=size,
                              color=color or self.color,
                              label=label or '{} ({:})'.format(self.name, self.epoch),
                              alpha=alpha,
                              edgecolor=edgecolor,
                              **kw)

        return scatter

    def finder(self, figsize=(7,7), **kwargs):
        '''
        Plot a finder chart. This *does* create a new figure.
        '''

        if (self.center is None) or (self.radius is np.inf):
            return self.allskyfinder(**kwargs)

        plt.figure(figsize=figsize)
        scatter = self.plot(**kwargs)
        plt.xlabel(r'Right Ascension ($^\circ$)'); plt.ylabel(r'Declination ($^\circ$)')
        #plt.title('{} in {:.1f}'.format(self.name, epoch))
        r = self.radius.to('deg')

        #center = self.coordinate_center
        #plt.xlim(center.ra + r/np.cos(center.dec), center.ra- r/np.cos(center.dec))
        #plt.ylim(center.dec - r, center.dec + r)

        ax = plt.gca()
        ax.set_aspect(1.0/np.cos(np.mean(self.dec)))

        return scatter

    def allskyfinder(self, figsize=(14, 7), **kwargs):
        '''
        Plot an all-sky finder chart. This *does* create a new figure.
        '''

        plt.figure(figsize=figsize)
        scatter = self.plot(**kwargs)
        plt.xlabel(r'Right Ascension ($^\circ$)'); plt.ylabel(r'Declination ($^\circ$)')
        #plt.title('{} in {:.1f}'.format(self.name, epoch))
        plt.xlim(0, 360)
        plt.ylim(-90,90)
        return scatter

    def animate(self, filename='constellation.mp4', epochs=[1900,2100], dt=5, dpi=300, fps=10, **kw):
        '''
        Animate a finder chart.
        '''

        scatter = self.finder(**kw)
        plt.tight_layout()
        figure = plt.gcf()

        if '.gif' in filename:
            try:
                writer = ani.writers['pillow'](fps=fps)
            except (RuntimeError, KeyError):
                writer = ani.writers['imagemagick'](fps=fps)
            except:
                raise RuntimeError('This python seems unable to make an animated gif.')
        else:
            try:
                writer = ani.writers['ffmpeg'](fps=fps)
            except (RuntimeError,KeyError):
                raise RuntimeError('This computer seems unable to ffmpeg.')


        with writer.saving(figure, filename, dpi or figure.get_dpi()):
            for epoch in tqdm(np.arange(epochs[0], epochs[1]+dt, dt)):

                # update the illustration to a new time
                coords = self.at_epoch(epoch)
                scatter.set_offsets(list(zip(coords.ra.value, coords.dec.value)))
                plt.title('{} in {:.1f}'.format(self.name, epoch))

                writer.grab_frame()


    def cross_match_to(self, reference, radius=1*u.arcsec, visualize=False):
        '''
        Cross-match this catalog onto another reference catalog.
        If proper motions are included in the reference, then
        its coordinates will be propagated to the obstime/epoch
        of this current catalog.

        Parameters
        ----------

        reference : Constellation
            A reference Constellation to which we want to
            cross-match the stars in this catalog. Most likely,
            you'll want to use Gaia for this (since it has
            good astrometry and good proper motions).

        radius : float, with astropy units of angle
            How close to objects need to be in the cross-match
            for them to be considered a matched pair?

        Returns
        -------

        i_this : array of indices
            The elements of this catalog that are matched.

        i_ref : array of indices
            The elements of the reference catalog, corresponding to
        '''

        # find the closest match for each of star in this constellation
        this = self.skycoord
        that = reference.at_epoch(self.obstime).skycoord
        i_ref, d2d_ref, d3d_ref = this.match_to_catalog_sky(that)

        # extract only those within the specified radius
        ok = d2d_ref < radius
        self.speak('found {} matches within {}'.format(np.sum(ok), radius))

        # make a plot, if desired
        if visualize:
            self.speak('p')
            plt.hist(d2d_ref.arcsec, range=(0,15))
            plt.axvline(radius.arcsec)
            plt.xlabel('Separation (arcsec)')
            plt.ylabel('Number of Matched Sources')

        # return the indices (of this, and of the reference) for the matches
        return ok, i_ref[ok]


"""    @classmethod
    def from_text(cls, filename, **kwargs):
        '''
        Create a constellation by reading a catalog in from a text file,
        as long as it's formated as in to_text() with identifiers, coordinates,
        magnitudes.

        Parameters
        ----------
        filename : str
            The filename to read in.

        **kwargs are passed to astropy.io.ascii.read()
        '''

        # FIXME -- add something here to parse id, mag, errors from the table!
        # this will be tricky, because right now we (foolishly) keep track
        # of what kinds of keys are what through class variables instead
        # of ones that can remain local to the instance

        # load the table
        t = ascii.read(filename, **kwargs)

        '''
        # which columns is the coordinates?
        i_coordinates = t.colnames.index('ra')

        # everything before the coordinates is an identifier
        identifiers = Table(t.columns[:i_coordinates])

        # the complete coordinates are stored in one
        c = t.columns[i_coordinates:i_coordinates+6]
        coordinates = SkyCoord(**c)
        coordinates.obstime=Time(cls.epoch, format='decimalyear')

        # everything after coordinates is magnitudes
        magnitudes = Table(t.columns[i_coordinates+1:])

        newtable = hstack([Table(identifiers),
                           Table({'coordinates':coordinates}),
                           Table(magnitudes)])
        '''
        this = cls(t) #, center=t.meta['center'], radius=t.meta['radius']
        this.speak('loaded constellation from {}'.format(filename))

        return this"""
