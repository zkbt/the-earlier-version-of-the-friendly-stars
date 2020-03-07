from .imports import *
from .constellations.constellation import *

def clean_tic_string(s):
    '''
    Be sure to strip the "TIC" out of a TIC.
    '''
    return int(str(s).lower().replace('tic', '').replace(' ', ''))

def get_one_star_as_constellation(star):
    '''
    Download the coordinates for a star, from a given name,
    using SkyCoord's name resolver (Simbad?).

    Parameters
    ----------
    star : str
        The name of the star to download.

    Returns
    -------
    s : Constellation
        A populated Constellation containing one star.
    '''

    # download that TIC from the archive
    try:
        t = SkyCoord.from_name(star)
    except NameResolveError:
        raise NameResolveError(f"""
        Oh no! We seem unable to use CDS to resolve the name '{star}'.

        Perhaps try another identifier for your star?
        """)

    t.obstime = Time('J2000.0')

    # define a constellation
    s = Constellation.from_skycoord(t)

    return s

def get_one_tic_as_constellation(tic):
    '''
    Use the MAST archive to download the coordinates (including proper
    motions) for one star from the TESS Input Catalog.

    Parameters
    ----------
    tic : str, int
        The TIC id of the star to download, with or without 'TIC' as a preface.

    Returns
    -------
    s : Constellation
        A populated Constellation containing one star.
    '''

    # import Catalogs only when we need it
    # (otherwise, we'll need the internet to ever run tfs)
    from astroquery.mast import Catalogs

    # download that TIC from the archive
    try:
        table =  Catalogs.query_criteria(catalog="Tic", ID=clean_tic_string(tic))
        assert(len(table) > 0)
    except (AttributeError, ValueError):
        raise NameResolveError(f"""
        Oh no! We seem unable to use astroquery to find an entry for '{tic}'.

        Are you sure it's a real entry in the TESS Input Catalog?
        """)

    # pull out a single row from the results
    t = table[0]

    # the 'ra' and 'dec' columns were propagated to J2000
    # (https://outerspace.stsci.edu/display/TESS/TIC+v8+and+CTL+v8.xx+Data+Release+Notes)
    obstime='J2000.0'

    # define a constellation, with proper motions and a time
    s = Constellation.from_coordinates(  ra=t['ra']*u.deg,
                                         dec=t['dec']*u.deg,
                                         pm_ra_cosdec=t['pmRA']*u.mas/u.year,
                                         pm_dec=t['pmDEC']*u.mas/u.year,
                                         obstime=obstime)
    return s

def parse_center(center):
    '''
    Flexible wrapper to ensure we return a center as a Constellation.

    Parameters
    ----------
    center : SkyCoord, str
    '''
    if isinstance(center, SkyCoord):
        if center.obstime is None:
            center.obstime = Time('J2000.0') # kludge?
        return Constellation.from_skycoord(center)
    elif isinstance(center, Constellation):
        return center
    elif type(center) == str:
        if center[0:3].lower() == 'tic':
            return get_one_tic_as_constellation(center)
        else:
            return get_one_star_as_constellation(center)
    else:
        raise NameResolveError(f"""
        Hmmmm...it doesn't seem totally clear how to parse the
        request for a star called '{center}'.

        Perhaps try another identifier for your star?
        """)
