"""
r.py: A python script containing functions to convert road polylines to a walking speed surface

Inspiration from:
https://gis.stackexchange.com/questions/221718/rasterizing-shapefile-with-attribute-value-as-pixel-value-with-gdal-in-python
https://www.datacamp.com/community/tutorials/fuzzy-string-python
"""

# Imports
import sys
sys.path.append('/home/s1891967/diss/code/Diss/')
from osgeo import ogr
import numpy as np
import pandas as pd
from fuzzywuzzy import process

from cpas.tifs import *

def backfill(arr, arr1):
    """To fill null values in array with values from another array

    Parameters
    ----------
    arr : np.array
        Array to fill with
    arr1 : np.array
        Array to fill

    Returns
    -------
    arr1
        Filled array
    """
    
    arr = np.where(arr < 0.01, np.NaN, arr)
    # FIXME:
    # RuntimeWarning: invalid value encountered in less
    # arr = np.where(arr < 0.01, np.NaN, arr)

    x = np.isnan(arr1)
    arr1[x] = arr[x]
    return arr1

def r_to_ws(road_fn, ws, paths, ta):
    """Converts road polylines to walking speed surface

    Parameters
    ----------
    roads : str
        The file location of the roads shapefile
    ws : str
        The file location of the csv file for roads walking speeds
    paths : bool
        A flag to indicate whether to include small paths 
    ta : obj
        An object holding empty in-memory raster to use in rasterization   

    Returns
    -------
    arr1
        An array of walking speeds
    """

    # Open the road data source and find distinct road classes from 'tag' field
    source_ds = ogr.Open(road_fn)
    source_layer = source_ds.GetLayer()
    feature = source_layer.GetNextFeature()
    field_vals = set([feature.GetFieldAsString('tag') for feature in source_layer])

    # Read excel file with walking speeds into pandas dataframe and sort
    costs = pd.read_csv(ws)
    costs = costs.sort_values(by=['Walking_Speed'], ascending=False)
    # TODO: Consider whether we should take into account congestion, crossings etc
    if paths is False:
        print()
    # TODO: if False remove paths from pandas dataframe.... 

    # blank array to use in first back fill
    arr1 = ta.dst_ds.GetRasterBand(1).ReadAsArray()

    # Loop through road costs dataframe
    for index, row in costs.iterrows():

        # use fuzzy match spreadsheet road classes to polyline road classes
        match = process.extractOne(row[0], field_vals)

        # create SQL string to select one polyline road class at a time
        # formatted string of SQL statement where match[0] = road feature class
        sql_str = f"SELECT * FROM AllRoads WHERE tag='{match[0]}'" 

        # rasterize one road class at a time using value from input csv
        # to in-memory array sized based on landcover input
        opt = gdal.RasterizeOptions(burnValues=row[1], # walking speed value to assign to pixel from input csv
                                    allTouched=True, # value assigned to all pixels touched by line
                                    SQLStatement=sql_str, # use above SQL string
                                    SQLDialect='SQLITE')
        gdal.Rasterize(ta.dst_ds, road_fn, options=opt) #(in-memory array, road shapefile, above options)

        # FIXME: 
        # Warning 1: The input vector layer has a SRS, but the output raster dataset SRS is unknown.
        # Ensure output raster dataset has the same SRS, otherwise results might be incorrect.

        # get array from in-memory rasterized layer
        arr = ta.dst_ds.GetRasterBand(1).ReadAsArray()

        # create one layer of all roads prioritising based on rasterizing order
        arr1 = backfill(arr, arr1)

    return arr1


if __name__ == '__main__':

    # Filename of input shapefile
    road_fn = '/home/s1891967/diss/Data/Input/OSM_roads/AllRoads.shp'

    # Excel file
    costsfile = '/home/s1891967/diss/Data/Input/Road_Costs.csv'

    # Output filename
    ws_out = '/exports/csce/datastore/geos/groups/cpas/all_roads.tif'

    #path to files
    p = '/home/s1891967/diss/Data/Input/'
    # Landcover
    lc_inp = p + 'UgandaLandCover/Uganda_Sentinel2_LULC2016.tif'

    paths = True

    # Read land cover tiff
    roads = tiffHandle(lc_inp)
    roads.readTiff(lc_inp)
    roads.emptyTiff()

    # Convert land cover to walking speeds
    roads.data = r_to_ws(road_fn, costsfile, paths, roads)

    # Write walking speeds tiff out
    roads.writeTiff(ws_out)



