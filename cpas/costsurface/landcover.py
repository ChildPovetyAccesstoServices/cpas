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

import numpy
import xarray
import pandas

def readLandcoverSpeedMap(fname, landcover='Code',
                          speed='Walking Speed (km/h)',
                          dropNaN=True, scale=None):
    """construct landcover to speed map

    Parameters
    ----------
    fname: name of csv file containing landcover to speed map
           the first row is assumed to contain column names
    landcover: the name of the column containing the landcover types
           default: 'Code'
    speed: the name of the column containing the speeds
           default: 'Walking Speed (km/h)'
    dropNaN: whether landtypes with NaN values should be dropped
           default: True
    scale: when set speed values will be scaled and turned into integers

    Returns
    -------
    tuple of two arrays containing the landcover type and the associated speed
    """

    costs = pandas.read_csv(fname)
    if dropNaN:
        costs.dropna(inplace=True)
    lc = numpy.array(costs[landcover])
    s = numpy.array(costs[speed])
    if scale:
        s = (numpy.round(s*scale)).astype(numpy.int64)
    return (lc,s)

def applyLandcoverSpeedMap(landcover: xarray.DataArray,speedmap) -> xarray.DataArray:
    """convert a landcover surface to a speed surface using a map

    Parameters
    ----------
    landcover:  a 2D xarray containg the landcover 
    map: a tuple with two arrays containing the landcover type and 
         associated speed

    Returns
    -------
    an xarray containing the speed surface
    """

    landcover_types,speed_values = speedmap
    
    speedsurface = xarray.zeros_like(landcover,dtype=numpy.float32)
    speedsurface.values[:] = numpy.nan
    
    # consider only pixels with interesting data
    mask = numpy.in1d(landcover.values,landcover_types)
    # create index into landcover_types
    idx = numpy.searchsorted(landcover_types,landcover.values.ravel()[mask])
    # assign speed values
    speedsurface.values.ravel()[mask] = speed_values[idx]

    return speedsurface
    
    
if __name__ == '__main__':
    import rioxarray

    
    lcmap = '/scratch/mhagdorn/cpas/test/inputs/Landcover_Costs.csv'
    speedmap = readLandcoverSpeedMap(lcmap)

    landtype = rioxarray.open_rasterio('/scratch/mhagdorn/cpas/test/inputs/UgandaLandCover/Uganda_Sentinel2_LULC2016.tif')
    
    speedsurface = applyLandcoverSpeedMap(landtype,speedmap)

    task = speedsurface.rio.to_raster('test.tif')

