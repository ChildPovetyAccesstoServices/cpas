# This file is part of cpas.
#
# cpas is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# cpas is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with cpas.  If not, see <https://www.gnu.org/licenses/>.
#
# Copyright (C) 2020 cpas team

__all__ = ['computeSlopeImpact']

import numpy
import xarray


def computePercentageSlope(dem):
    """compute percentage slope

    Parameters
    ----------
    dem: object containing the dem

    Returns
    -------
    array containing the percentage slope
    """

    dx = dem.differentiate('x')
    dy = dem.differentiate('y')
    # the scaling factor of 111120 converts degrees to metres.
    # this is a good approximation near the equator
    slope = (dx * dx + dy * dy) ** 0.5 * 100 / 111120
    return slope


def slopespeed(slopes):
    """Function to calculate road navigation speed

    See equation 4 from Irmischer and Clarke (2018).
    https://doi.org/10.1080/15230406.2017.1292150

    This models walking speed based on slope.

    Parameters
    ----------
    slopes: array holding slopes

    Returns
    -------
    0.11 + np.exp(((-(a + 5)**2)/(2*30**2)))
        Result of equation
    """

    def _model(x):
        return 0.11 + numpy.exp(((- (x + 5) ** 2) / (2 * 30 ** 2)))

    return xarray.apply_ufunc(_model, slopes)


def computeSlopeImpact(dem):
    """Function to calculate slope impact from DEM

    Parameters
    ----------
    dem: object holding digital elevation model

    Returns
    -------
    array of slope impact
    """

    slopes = computePercentageSlope(dem)

    # mask out slopes above 45 degree, ie 100%
    slopes = xarray.where(slopes >= 100, numpy.nan, slopes)

    # take the mean speed for both upwards and downwards slope.
    # relative to going along the flat (0 slope)

    slopes = 0.5 * (slopespeed(slopes) + slopespeed(-slopes)) / slopespeed(0)

    return slopes


if __name__ == '__main__':
    import rioxarray
    from cpas.config import CpasConfig
    import sys

    cfg = CpasConfig()
    cfg.read(sys.argv[1])

    dem = rioxarray.open_rasterio(cfg.dem, masked=True)
    landtype = rioxarray.open_rasterio(cfg.landcover, masked=True)

    slope_impact = computeSlopeImpact(dem).rio.reproject_match(landtype)

    slope_impact.rio.to_raster('slope_test.tif')
