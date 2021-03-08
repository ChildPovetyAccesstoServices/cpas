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

__all__ = ['readRoadSpeedMap', 'rasterizeAllRoads']

import numpy
import xarray
import pandas
from fuzzywuzzy import process
from rasterio import features


def readRoadSpeedMap(fname, road='Feature_Class',
                     speed='Walking_Speed',
                     dropNaN=True):
    """construct road type to speed map

    Parameters
    ----------
    fname: name of csv file containing road to speed map
           the first row is assumed to contain column names
    road: the name of the column containing the road types
           default: 'Feature_Class'
    speed: the name of the column containing the speeds
           default: 'Walking_Speed'
    dropNaN: whether road with NaN values should be dropped
           default: True

    Returns
    -------
    a pandas series containing speeds
    """

    costs = pandas.read_csv(fname, index_col=road)
    if dropNaN:
        costs = costs[costs[speed].notna()]
    return costs[speed]


def rasterizeRoads(roads, landcover, road_speed_map):
    """rasterize roads

    Parameters
    ----------
    roads: roads vector layer
    landcover: xarry used for creating empty array
    road_speed_map: dictionary mapping road type to travel speed

    Returns
    -------
    an xarray containing the speed surface
    """

    # construct filter selecting all roads of a particular type
    filtered = filter(lambda f: f['properties']['tag'] in road_speed_map,
                      roads)

    speedsurface = features.rasterize(
        ((f['geometry'],
          road_speed_map[f['properties']['tag']]) for f in filtered),
        out_shape=landcover.rio.shape,
        transform=landcover.rio.transform(),
        all_touched=True)

    return speedsurface


def rasterizeAllRoads(roads, landcover, road_speed_map, maxspeed=True):
    """rasterize all roads

    Parameters
    ----------
    roads: roads vector layer
    landcover: xarry used for creating empty array
    road_speed_map: pandas series containing speeds
    maxspeed: when set to False road types are not ordered and slower
              road speeds might override faster speeds

    Returns
    -------
    an xarray containing the speed surface
    """

    # extract road types from road shapefile
    road_types = set([feature['properties']['tag'] for feature in roads])

    # modify index so that it matches the road types in the vector layer
    idx = road_speed_map.index.to_list()
    for i, rt in enumerate(idx):
        matched_rt = process.extractOne(rt, road_types)[0]
        print(f'using matched road type {matched_rt} for {rt}')
        idx[i] = matched_rt
    road_speed_map.index = idx

    if maxspeed:
        rcost = rasterizeAllRoadsMax(roads, landcover, road_speed_map)
    else:
        rcost = rasterizeRoads(roads, landcover, road_speed_map.to_dict())

    # replace fill values with nans
    rcost = numpy.where(rcost == 0, numpy.nan, rcost)

    speedsurface = xarray.zeros_like(landcover, dtype=numpy.float32)
    speedsurface.values[0, :, :] = rcost[:, :]

    return speedsurface


def rasterizeAllRoadsMax(roads, landcover, road_speed_map):
    """rasterize all roads

    This version takes the largest speed when a pixel contains
    multiple roads

    Parameters
    ----------
    roads: roads vector layer
    landcover: xarry used for creating empty array
    road_speed_map: dictionary mapping road type to travel speed

    Returns
    -------
    a numpy arrray containing the speed surface
    """

    speedsurface = numpy.zeros(landcover.shape[1:], dtype=numpy.float32)

    # loop over unique speed values to group roads by speed
    for speed in road_speed_map.unique():
        # select all roads with that speed
        selected_roads = road_speed_map[road_speed_map == speed]
        rcost = rasterizeRoads(roads, landcover, selected_roads.to_dict())
        # take max values
        speedsurface = numpy.maximum(speedsurface, rcost)

    return speedsurface


if __name__ == '__main__':
    import fiona
    import rioxarray
    from cpas.config import CpasConfig
    import sys

    cfg = CpasConfig()
    cfg.read(sys.argv[1])

    road_speed_map = readRoadSpeedMap(cfg.roads_ws)

    roads = fiona.open(cfg.roads)
    landtype = rioxarray.open_rasterio(cfg.landcover, masked=True)

    speedsurface = rasterizeAllRoads(roads, landtype, road_speed_map)

    speedsurface.rio.to_raster('roads_test.tif')
