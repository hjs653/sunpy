# -*- coding: utf-8 -*-
import astropy.wcs.utils
from astropy.wcs import WCSSUB_CELESTIAL
from astropy.wcs import WCS

from .frames import BaseCoordinateFrame, Helioprojective, Heliocentric, HeliographicStonyhurst, HeliographicCarrington

__all__ = ['solar_wcs_frame_mapping', 'solar_frame_to_wcs_mapping']


def solar_wcs_frame_mapping(wcs):
    """
    This function registers the coordinates frames to their FITS-WCS coordinate
    type values in the `astropy.wcs.utils.wcs_to_celestial_frame` registry.
    """

    dateobs = wcs.wcs.dateobs if wcs.wcs.dateobs else None

    # SunPy Map adds 'heliographic_observer' and 'rsun' attributes to the WCS
    # object. We check for them here, and default to None.
    if hasattr(wcs, 'heliographic_observer'):
        observer = wcs.heliographic_observer
    else:
        observer = None

    if hasattr(wcs, 'rsun'):
        rsun = wcs.rsun
    else:
        rsun = None

    # First we try the Celestial sub, which rectifies the order.
    # It will return anything matching ??LN*, ??LT*
    wcss = wcs.sub([WCSSUB_CELESTIAL])

    # If the SUB works, use it.
    if wcss.naxis == 2:
        wcs = wcss

    xcoord = wcs.wcs.ctype[0][0:4]
    ycoord = wcs.wcs.ctype[1][0:4]

    if xcoord == 'HPLN' and ycoord == 'HPLT':
        return Helioprojective(obstime=dateobs, observer=observer, rsun=rsun)

    if xcoord == 'HGLN' and ycoord == 'HGLT':
        return HeliographicStonyhurst(obstime=dateobs)

    if xcoord == 'CRLN' and ycoord == 'CRLT':
        return HeliographicCarrington(obstime=dateobs)

    if xcoord == 'SOLX' and ycoord == 'SOLY':
        return Heliocentric(obstime=dateobs, observer=observer)


def solar_frame_to_wcs_mapping(frame, projection='TAN'):
    """
    For a given frame, this function returns the corresponding WCS object.
    It registers the WCS coordinates types from their associated frame in the
    `astropy.wcs.utils.celestial_frame_to_wcs` registry.
    """
    wcs = WCS(naxis=2)

    if hasattr(frame, 'rsun'):
        wcs.rsun = frame.rsun
    else:
        wcs.rsun = None

    if hasattr(frame, 'observer'):
        wcs.heliographic_observer = frame.observer

    if isinstance(frame, BaseCoordinateFrame):

        wcs.wcs.dateobs = frame.obstime.utc.isot
        if isinstance(frame, Helioprojective):
            xcoord = 'HPLN' + '-' + projection
            ycoord = 'HPLT' + '-' + projection
            wcs.wcs.cunit = ['arcsec', 'arcsec']
        elif isinstance(frame, Heliocentric):
            xcoord = 'SOLX'
            ycoord = 'SOLY'
            wcs.wcs.cunit = ['arcsec', 'arcsec']
        elif isinstance(frame, HeliographicStonyhurst):
            xcoord = 'HGLN' + '-' + projection
            ycoord = 'HGLT' + '-' + projection
            wcs.wcs.cunit = ['deg', 'deg']
        elif isinstance(frame, HeliographicCarrington):
            xcoord = 'CRLN' + '-' + projection
            ycoord = 'CRLT' + '-' + projection
            wcs.wcs.cunit = ['deg', 'deg']
    else:
        return None

    wcs.wcs.ctype = [xcoord, ycoord]

    return wcs

astropy.wcs.utils.WCS_FRAME_MAPPINGS.append([solar_wcs_frame_mapping])
astropy.wcs.utils.FRAME_WCS_MAPPINGS.append([solar_frame_to_wcs_mapping])
