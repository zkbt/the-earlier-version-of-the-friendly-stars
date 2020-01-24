from .constellation import *
from ..field import Field

class CatalogConstellation(Constellation, Field):
    def __init__(self,
                 center,
                 radius=3*u.arcmin,
                 **kw):
        '''
        Initialize a Constellation from a search of the sky, usually
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

        # parse the ways in which someone could be asking for an all-sky query
        if np.isfinite(radius) is False:
            center = None
        if center is None:
            radius = np.inf

        # assign the center and the radius for this cone
        Field.__init__(self, center, radius)

        # poulate the ._downloaded attribute (either by loading or downloading)
        self.populate()

        # feed a standardized table as inputs to create a constellation
        Constellation.__init__(self, self._downloaded,
                               center=self.center, radius=self.radius)
