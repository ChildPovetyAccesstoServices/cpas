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

import sys

import rioxarray
import fiona
import xarray
import numpy
from . import costsurface
from .config import CpasConfig


def speed_to_cost(speed, child_impact=1):
    """
    convert speed surface to cost surface

    Parameters
    ----------
    speed: object containing the speed surface
          in km/h
    child_impact: factor applied when traveling
          with a child (default=1))

    Return
    ------
    cost surface
    """

    # apply child impact factor and convert to m/s
    cost = speed * child_impact * 1000 / 3600
    # compute the costsurface, ie time.
    # the factor 111120 converts degree to m close to the equator
    return abs(speed.rio.resolution()[0]) * 111120 / cost


def main():

    cfg = CpasConfig()
    cfg.read(sys.argv[1])

    # load the landcover - speedmap and the landcover dataset
    lc_speedmap = costsurface.readLandcoverSpeedMap(cfg.landcover_ws)
    landcover = rioxarray.open_rasterio(cfg.landcover, masked=True)
    # compute the speed surface due to the landcover
    lws = costsurface.applyLandcoverSpeedMap(landcover, lc_speedmap)

    # load the road - speedmap and the road dataset
    r_speedmap = costsurface.readRoadSpeedMap(cfg.roads_ws)
    roads = fiona.open(cfg.roads)
    rws = costsurface.rasterizeAllRoads(roads, landcover, r_speedmap)

    # compute the slope impact and resample it
    dem = rioxarray.open_rasterio(cfg.dem,
                                  masked=True).rio.reproject_match(lws)
    slope_impact = costsurface.computeSlopeImpact(dem)
    # make sure coordinates are the same
    # there might be some numerical noise after reprojecting the data
    slope_impact['x'] = lws['x']
    slope_impact['y'] = lws['y']

    # combine the two speed surfaces
    ws = xarray.where(rws.notnull(), rws, lws)

    # compute cost surface
    cs = speed_to_cost(ws * slope_impact, cfg.child_impact)

    # write costsurface
    cs.rio.to_raster(cfg.costsurface)

    # consider water being passable
    # 10 is the code for open water
    water = xarray.where(landcover == 10, cfg.waterspeed, numpy.NaN)
    # convert water speed to time
    # 1 as children arnt slower than adults on motor boats...
    water = speed_to_cost(water)
    cs = xarray.where(water.notnull(), water, cs)

    # write output
    cs.rio.to_raster(cfg.costsurface_water)


if __name__ == '__main__':
    main()
