from ..imports import *
from astropy.table import hstack

# a shortcut getting the coordinates for an object, by its name
get = coord.SkyCoord.from_name

def parse_center(center):
    if type(center) == str:
        center = get(center)
    return center

class Constellation(Talker):
    '''
    A Constellation is collection of stars
    that can be accessed through a table of
    astropy coordinates, and/or plotted
    on a Finder chart Panel.
    '''
    name = 'someconstellation'
    color = 'black'
    epoch = 2000.0 # the default epoch
    magnitudelimit = np.inf
    identifier_keys = []
    error_keys = []
    coordinate_keys = ['ra', 'dec', 'distance', 'pm_ra_cosdec', 'pm_dec', 'radial_velocity', 'obstime']
    def __init__(self, standardized):
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
        #self.identifiers = self.standardized[[i + '-id' for i in self.identifier_keys]]
        #self.coordinates = self.standardized['coordinates']
        #self.magnitudes = self.standardized[[f+'-mag' for f in self.filters]]

        # use the first identifier as the search key
        self.standardized.add_index(self.identifier_keys[0]+'-id')

        # set up some shortcuts
        for k in self.coordinate_keys:
            vars(self)[k] = self.standardized[k]

        #
        self.epoch = self.obstime.to('year').value
        if (self.epoch == self.epoch[0]).all():
            self.epoch = self.epoch[0]

        # summarize the stars in this constellation
        self.speak('{} contains {} objects'.format(self.name, len(self.standardized)))

    @property
    def coordinates(self):
        return  self.standardized[self.coordinate_keys]

    @property
    def identifiers(self):
        return self.standardized[[i + '-id' for i in self.identifier_keys]]

    @property
    def magnitudes(self):
        return self.standardized[[f+'-mag' for f in self.filters]]

    @property
    def errors(self):
        if len(self.error_keys) > 0:
            return self.standardized[[e + '-error' for e in self.error_keys]]


    def find(self, id):
        return self.__class__(Table(self.standardized.loc[id]))

    def __getitem__(self,x):
        trimmed = Table(self.standardized[x])
        return self.__class__(trimmed)

    def _coordinate_table(self):
        c = self.coordinates
        N = len(c.icrs.ra)
        return Table(data=[c.icrs.ra,
                           c.icrs.dec,
                           c.distance,
                           c.pm_ra_cosdec,
                           c.pm_dec,
                           c.radial_velocity,
                           c.obstime.decimalyear*np.ones(N)],
                     names=['ra',
                            'dec',
                            'distance',
                            'pm_ra_cosdec',
                            'pm_dec',
                            'radial_velocity',
                            'obstime'])

    def to_text(self, filename=None, overwrite=True):
        '''
        Write this catalog out to a text file.
        '''

        table = self.standardized
        #table = hstack([self.identifiers,
        #                self._coordinate_table(),
        #                self.magnitudes,
        #                self.errors])

        if filename == None:
            filename = '{}.txt'.format(self.name)
        self.speak('saving to {}'.format(filename))
        table.write(filename, format='ascii.ecsv', overwrite=overwrite)

    @classmethod
    def from_text(cls, filename, **kwargs):
        '''
        Create a constellation by reading a catalog in from a text file,
        as long as it's formated as in to_text() with identifiers, coordinates, magnitudes.

        Parameters
        ----------
        filename : str
            The filename to read in.

        **kwargs are passed to astropy.io.ascii.read()
        '''

        # FIXME -- add something here to parse id, mag, errors from the table?

        # load the table
        t = ascii.read(filename, **kwargs)

        '''
        # which columns is the coordinates?
        i_coordinates = t.colnames.index('ra')

        # everything before the coordinates is an identifier
        identifiers = Table(t.columns[:i_coordinates])

        # the complete coordinates are stored in one
        c = t.columns[i_coordinates:i_coordinates+6]
        coordinates = coord.SkyCoord(**c)
        coordinates.obstime=Time(cls.epoch, format='decimalyear')

        # everything after coordinates is magnitudes
        magnitudes = Table(t.columns[i_coordinates+1:])

        newtable = hstack([Table(identifiers),
                           Table({'coordinates':coordinates}),
                           Table(magnitudes)])
        '''
        this = cls(t)
        this.speak('loaded constellation from {}'.format(filename))

        return this

    @property
    def magnitude(self):
        return self.magnitudes[self.defaultfilter+'-mag']

    def atEpoch(self, epoch=2000):
        '''
        Return SkyCoords of the objects, propagated to a (single) given epoch.

        Parameters
        ----------
        epoch : Time, or float
            Either an astropy time, or a decimal year of the desired epoch.

        Returns
        -------
        coordinates : SkyCoord(s)
            The coordinates, propagated to the given epoch,
            with that epoch stored in the obstime attribute.
        '''

        projected = copy.deepcopy(self.standardized)

        # calculate the time offset from the epochs of the orignal coordinates
        try:
            epoch.year
            newobstime = epoch
        except AttributeError:
            try:
                newobstime = epoch.decimalyear*u.year
            except AttributeError:
                newobstime = epoch*u.year

        #with warnings.catch_warnings() :
        #    warnings.filterwarnings("ignore")
        #    newobstime = Time(year, format='decimalyear')
        #    dt = newobstime - self.obstime
        dt = newobstime - self.obstime

        # calculate the new positions, propagated linearly by dt
        try:
            # if proper motions exist
            newra = (self.ra + self.pm_ra_cosdec/np.cos(self.dec)*dt).to(u.deg)
            newdec = (self.dec + self.pm_dec*dt).to(u.deg)
        except TypeError:
            # assume no proper motions, if they're not defined
            newra = self.ra
            newdec = self.dec
            self.speak('no proper motions were used for {}'.format(self.name))

        projected['ra'] = newra
        projected['dec'] = newdec
        projected['obstime'] = newobstime

        # return as SkyCoord object
        return self.__class__(projected) #coord.SkyCoord(ra=newra, dec=newdec, obstime=newobstime)

    def plot(self, epoch=2000.0, sizescale=10, color=None, alpha=0.5, label=None, edgecolor='none', **kw):
        '''
        Plot the ra and dec of the coordinates,
        at a given epoch, scaled by their magnitude.

        (This does *not* create a new empty figure.)

        Parameters
        ----------
        epoch : Time, or float
            Either an astropy time, or a decimal year of the desired epoch.
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

        # pull out the coordinates at this epoch
        coords = self.atEpoch(epoch)

        # calculate the sizes of the stars (logarithmic with brightness?)
        size = np.maximum(sizescale*(1 + self.magnitudelimit - self.magnitude), 0)

        # make a scatter plot of the RA + Dec
        scatter = plt.scatter(coords.ra, coords.dec,
                                    s=size,
                                    color=color or self.color,
                                    label=label or '{} ({:.1f})'.format(self.name, epoch),
                                    alpha=alpha,
                                    edgecolor=edgecolor,
                                    **kw)

        return scatter

    def finder(self, epoch=2015.5, figsize=(7,7), **kwargs):
        '''
        Plot a finder chart. This *does* create a new figure.
        '''

        try:
            self.center
        except AttributeError:
            return self.allskyfinder(epoch=epoch, **kwargs)

        plt.figure(figsize=figsize)
        scatter = self.plot(epoch=epoch, **kwargs)
        plt.xlabel(r'Right Ascension ($^\circ$)'); plt.ylabel(r'Declination ($^\circ$)')
        #plt.title('{} in {:.1f}'.format(self.name, epoch))
        r = self.radius.to('deg').value
        plt.xlim(self.center.ra.deg + r/np.cos(self.center.dec), self.center.ra.deg - r/np.cos(self.center.dec))
        plt.ylim(self.center.dec.deg - r, self.center.dec.deg + r)
        plt.gca().set_aspect(1.0/np.cos(self.center.dec))
        return scatter

    def allskyfinder(self, epoch=2015.5, figsize=(14, 7), **kwargs):
        '''
        Plot an all-sky finder chart. This *does* create a new figure.
        '''

        plt.figure(figsize=figsize)
        scatter = self.plot(epoch=epoch, **kwargs)
        plt.xlabel(r'Right Ascension ($^\circ$)'); plt.ylabel(r'Declination ($^\circ$)')
        plt.title('{} in {:.1f}'.format(self.name, epoch))
        plt.xlim(0, 360)
        plt.ylim(-90,90)
        return scatter

    def animate(self, filename='constellation.mp4', epochs=[1900,2100], dt=5, dpi=300, fps=10, **kw):
        '''
        Animate a finder chart.
        '''

        scatter = self.finder(epochs[0], **kw)
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
                coords = self.atEpoch(epoch)
                scatter.set_offsets(list(zip(coords.ra.value, coords.dec.value)))
                plt.title('{} in {:.1f}'.format(self.name, epoch))

                writer.grab_frame()

    def separation(self, epoch=2000, center=None):
        if center is None:
            center = self.center
        if epoch is None:
            epoch = self.epoch

        return self.atEpoch(epoch).separation(center)

    def crossMatchTo(self, reference, radius=1*u.arcsec, visualize=False):
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
        i_ref, d2d_ref, d3d_ref = self.coordinates.match_to_catalog_sky(reference.atEpoch(self.coordinates.obstime))

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
