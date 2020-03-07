
'''
Panel object contains
up to one image in the background,
and any number of catalogs plotted.
'''

from ..field import Field
from ..imports import *
from illumination import imshowFrame

class ImageUnavailableError(ValueError):
    pass

class Image(Field):
    '''
    This represents images that lines up
    with a given patch of the sky.
    '''

    def derive_pix2local(self):
        '''
        For this image, derive a linear transformation
        between pixels coordinates (x, y) in pixels
        and local coordinates (xi, eta) in arcmin
        (with astropy units attached).
        '''

        # create a grid of x and y pairs that span the whole image
        rows, cols = self.data.shape
        N = 10

        # numpy arrays are 0 as a convention?
        convention = 0

        # create a grid of pixels across the whole image
        y1d = np.linspace(0, rows, N)
        x1d = np.linspace(0, cols, N)
        x2d, y2d = np.meshgrid(x1d, y1d)

        # map those pixels to celestial (using all distortions in the WCS)
        ra, dec = self.wcs.all_pix2world(x2d, y2d, convention)

        # and then to local angles
        xi, eta = self.celestial2local(ra*u.deg, dec*u.deg)


        r'''
        How do we transform from $(x, y)$ to $(\xi, \eta)$? We want that to be
        an affine transformation, with the form:
        $$ \xi = ax + by + c $$
        $$ \eta = dx + ey + f $$
        to simplify our transformation into a completely linear one, that
        matplotlib can handle. So, let's do a linear fit to a grid of values...
        '''

        # what do we want to fit?
        xi_fit = xi.flatten().to('arcmin').value
        eta_fit = eta.flatten().to('arcmin').value

        # create a design matrix
        M = np.zeros((N**2, 3))
        M[:, 0] = x2d.flatten()
        M[:, 1] = y2d.flatten()
        M[:, 2] = 1

        # create a uniform inverse covariance matrix (equal weighting)
        C_inv = np.eye(N**2)

        # do a linear least squares fit for xi = a*x + c*y + e
        theta = np.linalg.inv(M.T @ C_inv @ M) @ (M.T @ C_inv @ xi_fit)
        a, c, e = theta

        # do a linear least squares fit for eta = b*x + d*y + f
        theta = np.linalg.inv(M.T @ C_inv @ M) @ (M.T @ C_inv @ eta_fit)
        b, d, f = theta

        # create the affine transformations
        self._pix2local = Affine2D.from_values(a, b, c, d, e, f)
        self._local2pix = self._pix2local.inverted()

        # check for really bad errors
        x_trans, y_trans = self._local2pix.transform(np.transpose([xi_fit, eta_fit])).T
        x_resid = x2d.flatten() - x_trans
        y_resid= y2d.flatten() - y_trans
        x_worst = np.max(np.abs(x_resid))
        y_worst = np.max(np.abs(y_resid))
        if (x_worst > 1) or (y_worst > 1):
            raise Warning(f'''
            The affine approximation to the WCS yields
            errors exceeding 1 pixel. The errors get as
            bad as dx={x_worst} and dy={y_worst}.

            Please make sure you feel OK about that,
            and then feel free to ignore this warning.
            ''')

    @property
    def pix2local(self):
        '''
        This transform takes pixels as input,
        and returns local sky coordinates.
        '''
        try:
            return self._pix2local
        except AttributeError:
            self.derive_pix2local()
            return self._pix2local

    @property
    def local2pix(self):
        '''
        This transform takes local sky coordinates
        as input, and returns image pixels.
        '''
        try:
            return self._local2pix
        except AttributeError:
            self.derive_pix2local()
            return self._local2pix


    def imshow(self, gridspec=None, share=None, transform=None):
        '''
        Plot this image as an imshow.
        (FIXME -- remove this once everything has been incorporated into )

        Parameters
        ----------
        gridspec : matplotlib.gridspec.SubplotSpec
            Should this image go into an existing spot?
        share : matplotlib.axes._subplots.AxesSubplot
            Should this imshow share the same axes
            limits as another existing axes?
        '''


        # replace this with an illumination frame?!
        inputs = dict(sharex=share, sharey=share)

        # this is where we will create the axes
        if gridspec is None:
            ax = plt.subplot(**inputs)
        else:
            ax = plt.subplot(gridspec, **inputs)

        # a quick normalization for the colors
        norm = plt.matplotlib.colors.SymLogNorm(
                              linthresh=mad_std(self.data),
                              linscale=1,
                              vmin=-np.max(self.data),
                              vmax=np.max(self.data))


        # create the imshow
        ax.imshow(self.data, origin='lower',
                             cmap='RdBu',
                             norm=norm,
                             transform=self.pix2local + ax.transData)


        # set the title of the axes
        ax.set_title(f'{self.survey} ({self.epoch:.0f})')

        # set some reasonable-ish initial defaults for the plotting limits
        r = self.radius.to('deg')
        ax.set_xlim(-r, r)
        ax.set_ylim(-r, r)

        return ax
