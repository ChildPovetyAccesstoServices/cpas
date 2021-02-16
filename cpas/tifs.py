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

'''

A class to handle geotiffs

inspired by OOSA
'''

#######################################################

# import necessary packages
from pyproj import Proj, transform  # package for reprojecting data
from osgeo import gdal  # pacage for handling geotiff data
from osgeo import osr  # pacage for handling projection information
from gdal import Warp
import numpy as np


#######################################################

class tiffHandle():
    '''

  Class to handle geotiff files

  '''

    ########################################

    def __init__(self, filename):
        '''

    Class initialiser
    Does nothing as this is only an example

    '''

    ########################################

    def writeTiff(self, filename="chm.tif", epsg=4326):  # deleted data??

        '''

    Write a geotiff from a raster layer

    '''
        #  change to resolution
        self.res = self.pixelWidth

        # Get those x's and y's
        self.minX = self.xOrigin
        self.maxY = self.yOrigin # tiff coordinates different way round

        # set geolocation information (note geotiffs count down from top edge in Y)
        geotransform = (self.minX, self.res, 0, self.maxY, 0, -1 * self.res)

        # load data in to geotiff object
        dst_ds = gdal.GetDriverByName('GTiff').Create(filename, self.nX, self.nY, 1, gdal.GDT_Float32)
        dst_ds.SetGeoTransform(geotransform)  # specify coords
        srs = osr.SpatialReference()  # establish encoding
        srs.ImportFromEPSG(epsg)  # WGS84 lat/long
        dst_ds.SetProjection(srs.ExportToWkt())  # export coords to file
        dst_ds.GetRasterBand(1).WriteArray(self.data)  # write image to the raster
        dst_ds.GetRasterBand(1).SetNoDataValue(-9999)  # set no data value
        dst_ds.FlushCache()  # write to disk
        dst_ds = None

        print("Image written to", filename)

        return

    ########################################

    def readTiff(self, filename, epsg=4326):
        '''

    Read a geotiff in to RAM

    '''

        # open a dataset object

        ds = gdal.Open(filename)

        # could use gdal.Warp to reproject if wanted?
        self.proj = ds.GetProjection()

        # read data from geotiff object
        self.nX = ds.RasterXSize  # number of pixels in x direction
        self.nY = ds.RasterYSize  # number of pixels in y direction

        # geolocation tiepoint
        transform_ds = ds.GetGeoTransform()  # extract geolocation information
        self.xOrigin = transform_ds[0]  # coordinate of x corner
        self.yOrigin = transform_ds[3]  # coordinate of y corner
        self.pixelWidth = transform_ds[1]  # resolution in x direction
        self.pixelHeight = transform_ds[5]  # resolution in y direction
        # read data. Returns as a 2D numpy array
        self.data = ds.GetRasterBand(1).ReadAsArray(0, 0, self.nX, self.nY) # you could utilise these to batch process the tif

#######################################################

    def emptyTiff(self):

        '''

    Write a empty memory array

    '''
        #  change to resolution
        self.res = self.pixelWidth

        # Get those x's and y's
        self.minX = self.xOrigin
        self.maxY = self.yOrigin # tiff coordinates different way round

        # set geolocation information (note geotiffs count down from top edge in Y)
        geotransform = (self.minX, self.res, 0, self.maxY, 0, -1 * self.res)

        # load data in to geotiff object
        self.dst_ds = gdal.GetDriverByName('MEM').Create('', self.nX, self.nY, 1, gdal.GDT_Float32)
        self.dst_ds.SetGeoTransform(geotransform)  # specify coords

        arr = self.dst_ds.GetRasterBand(1).ReadAsArray()
        arr = np.where(arr == 0.0, np.NaN, arr)

        self.dst_ds.GetRasterBand(1).WriteArray(arr)  # write image to the raster
