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

__all__ = ['readRoadSpeedMap','rasterizeAllRoads']

import numpy
import xarray
import pandas
from fuzzywuzzy import process
from rasterio import features

def readRoadSpeedMap(fname,road='Feature_Class',
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
    dictionary mapping road type to travel speed
    """

    costs = pandas.read_csv(fname,index_col=road)
    if dropNaN:
        costs = costs[costs[speed].notna()]
    return costs[speed].to_dict()

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
    filtered = filter(lambda f: f['properties']['tag'] in road_speed_map, roads)             

    speedsurface = features.rasterize(
        ((f['geometry'],
          road_speed_map[f['properties']['tag']]) for f in filtered),
        out_shape = landcover.rio.shape,
        transform = landcover.rio.transform(),
        all_touched = True)
    
    return speedsurface

def rasterizeAllRoads(roads, landcover, road_speed_map):
    """rasterize all roads

    Parameters
    ----------
    roads: roads vector layer
    landcover: xarry used for creating empty array
    road_speed_map: dictionary mapping road type to travel speed

    Returns
    -------
    an xarray containing the speed surface
    """
    
    # extract road types from road shapefile
    road_types = set([feature['properties']['tag'] for feature in roads])
    
    # create new road speed map matching the keys to the road types in vector layer
    road_speed_map_matched = {}
    for rt in road_speed_map:
        matched_rt = process.extractOne(rt,road_types)[0]
        road_speed_map_matched[matched_rt] = road_speed_map[rt]

    rcost = rasterizeRoads(roads,landtype,road_speed_map_matched)
    # replace fill values with nans
    rcost = numpy.where(rcost == 0, numpy.nan, rcost)

    speedsurface = xarray.zeros_like(landtype,dtype=numpy.float32)
    speedsurface.values[0,:,:] = rcost[:,:]

    return speedsurface
    
if __name__ == '__main__':
    import fiona
    import rioxarray
    
    road_speed_map = readRoadSpeedMap('/scratch/mhagdorn/cpas/test/inputs/Road_Costs.csv')

    roads = fiona.open('/scratch/mhagdorn/cpas/test/inputs/OSM_roads/AllRoads.shp')
    landtype = rioxarray.open_rasterio('/scratch/mhagdorn/cpas/test/inputs/UgandaLandCover/Uganda_Sentinel2_LULC2016.tif')

    # extract road types from road shapefile
    #road_types = set([feature['properties']['tag'] for feature in roads])
    road_types = {'track_grade2', 'trunk_link', 'track_grade4', 'motorway_link', 'path', 'steps', 'tertiary',
                  'primary_link', 'service', 'living_street', 'tertiary_link', 'track_grade5', 'primary',
                  'residential', 'motorway', 'cycleway', 'bridleway', 'unknown', 'track', 'trunk', 'track_grade1',
                  'unclassified', 'pedestrian', 'secondary_link', 'footway', 'track_grade3', 'secondary'}

    speedsurface = rasterizeAllRoads(roads, landtype, road_speed_map)

    speedsurface.rio.to_raster('test2.tif')
